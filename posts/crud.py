import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from posts.models import Post, Comment, Like
from posts.schemas import PostCreate, CommentCreate, PostOut, CommentOut
from redis_client import get_redis
from datetime import datetime

async def get_post_cache_key(post_id: int):
    return f"post:{post_id}:data"

async def get_comments_cache_key(post_id: int):
    return f"post:{post_id}:comments"

async def get_likes_count_key(post_id: int):
    return f"post:{post_id}:likes_count"

async def get_comments_count_key(post_id: int):
    return f"post:{post_id}:comments_count"

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

async def create_post(db: AsyncSession, post_in: PostCreate, user_id: int):
    new_post = Post(**post_in.model_dump(), user_id=user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post

async def create_comment(db: AsyncSession, post_id: int, comment_in: CommentCreate, user_id: int):
    # Verify post exists
    post_query = await db.execute(select(Post).where(Post.id == post_id))
    post = post_query.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(**comment_in.model_dump(), post_id=post_id, user_id=user_id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    # Redis caching
    redis = await get_redis()
    if redis:
        comment_dict = {
            "id": new_comment.id,
            "post_id": new_comment.post_id,
            "user_id": new_comment.user_id,
            "content": new_comment.content,
            "created_at": new_comment.created_at.isoformat()
        }
        
        # Add to list and keep only last 10
        comments_key = await get_comments_cache_key(post_id)
        await redis.lpush(comments_key, json.dumps(comment_dict))
        await redis.ltrim(comments_key, 0, 9)
        
        # Increment comment count
        count_key = await get_comments_count_key(post_id)
        await redis.incr(count_key)

    return new_comment

async def toggle_like(db: AsyncSession, post_id: int, user_id: int):
    # Verify post exists
    post_query = await db.execute(select(Post).where(Post.id == post_id))
    post = post_query.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_query = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    existing_like = like_query.scalar_one_or_none()

    redis = await get_redis()
    likes_count_key = await get_likes_count_key(post_id)

    if existing_like:
        db.delete(existing_like)
        await db.commit()
        if redis:
            await redis.decr(likes_count_key)
        return {"msg": "Post unliked"}
    else:
        new_like = Like(post_id=post_id, user_id=user_id)
        db.add(new_like)
        await db.commit()
        if redis:
            await redis.incr(likes_count_key)
        return {"msg": "Post liked"}

async def get_post_details(db: AsyncSession, post_id: int):
    redis = await get_redis()
    
    post_data = None
    last_comments = []
    likes_count = 0
    comments_count = 0

    if redis:
        post_key = await get_post_cache_key(post_id)
        cached_post = await redis.get(post_key)
        
        if cached_post:
            post_data = json.loads(cached_post)
        
        # Get counts
        likes_c = await redis.get(await get_likes_count_key(post_id))
        if likes_c: likes_count = int(likes_c)

        comments_c = await redis.get(await get_comments_count_key(post_id))
        if comments_c: comments_count = int(comments_c)

        # Get last 10 comments
        cached_comments = await redis.lrange(await get_comments_cache_key(post_id), 0, 9)
        last_comments = [json.loads(c) for c in cached_comments]

    # If post not in cache, fetch from DB
    if not post_data:
        post_query = await db.execute(select(Post).where(Post.id == post_id))
        post = post_query.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "created_at": post.created_at.isoformat()
        }
        
        if redis:
            await redis.set(await get_post_cache_key(post_id), json.dumps(post_data), ex=3600) # Cache for 1 hour

    # If we didn't have counts in redis, let's sync them from DB
    if redis and not await redis.exists(await get_likes_count_key(post_id)):
        likes_q = await db.execute(select(func.count(Like.id)).where(Like.post_id == post_id))
        likes_count = likes_q.scalar()
        await redis.set(await get_likes_count_key(post_id), likes_count)

    if redis and not await redis.exists(await get_comments_count_key(post_id)):
        comments_q = await db.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id))
        comments_count = comments_q.scalar()
        await redis.set(await get_comments_count_key(post_id), comments_count)
        
        # Load last 10 comments to cache
        last_comments_q = await db.execute(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.desc()).limit(10)
        )
        db_comments = last_comments_q.scalars().all()
        last_comments = [
            {
                "id": c.id,
                "post_id": c.post_id,
                "user_id": c.user_id,
                "content": c.content,
                "created_at": c.created_at.isoformat()
            } for c in db_comments
        ]
        
        # Push to redis list
        if db_comments:
            comments_key = await get_comments_cache_key(post_id)
            # Push in reverse to maintain order correctly since lpush pushes to head
            for c in reversed(last_comments):
                await redis.lpush(comments_key, json.dumps(c))

    return {
        **post_data,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "last_comments": last_comments
    }

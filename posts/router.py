from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from users.auth import get_current_user
from users.models import User
from posts.schemas import PostCreate, PostOut, CommentCreate, CommentOut, PostDetailOut
from posts.crud import create_post, create_comment, toggle_like, get_post_details

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    post_in: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_post(db, post_in, current_user.id)

@router.get("/{post_id}", response_model=PostDetailOut)
async def read_post_details(post_id: int, db: AsyncSession = Depends(get_db)):
    return await get_post_details(db, post_id)

@router.post("/{post_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_comment(db, post_id, comment_in, current_user.id)

@router.post("/{post_id}/likes")
async def like_or_unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await toggle_like(db, post_id, current_user.id)

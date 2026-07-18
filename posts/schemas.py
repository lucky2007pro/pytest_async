from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LikeOut(BaseModel):
    id: int
    post_id: int
    user_id: int

    class Config:
        from_attributes = True

class PostDetailOut(PostOut):
    likes_count: int
    comments_count: int
    last_comments: List[CommentOut] = []

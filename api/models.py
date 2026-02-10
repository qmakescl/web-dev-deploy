from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime

# --- User Models ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Post Models ---
class PostBase(BaseModel):
    content: Optional[str] = None

class PostCreate(PostBase):
    # Image file will be handled separately in multipart/form-data
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    img_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    like_count: int = 0
    comment_count: int = 0
    is_liked: bool = False

    class Config:
        from_attributes = True

# --- Interaction Models ---
class CommentBase(BaseModel):
    comment: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    post_id: int
    user_id: int
    liked: bool

# --- Tag Models ---
class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

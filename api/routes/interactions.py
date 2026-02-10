from fastapi import APIRouter, HTTPException, status, Depends
from ..models import CommentCreate, CommentResponse, LikeResponse
from ..database import db
from ..auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/{id}/like", response_model=LikeResponse)
async def toggle_like(id: int, current_user: dict = Depends(get_current_user)):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            # 게시글 존재 확인
            cur.execute("SELECT id FROM posts WHERE id = %s", (id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
            
            # 좋아요 여부 확인
            cur.execute("SELECT id FROM likes WHERE post_id = %s AND user_id = %s", (id, current_user["id"]))
            like = cur.fetchone()
            
            if like:
                cur.execute("DELETE FROM likes WHERE id = %s", (like["id"],))
                liked = False
            else:
                cur.execute("INSERT INTO likes (post_id, user_id) VALUES (%s, %s)", (id, current_user["id"]))
                liked = True
            
            conn.commit()
            return {"post_id": id, "user_id": current_user["id"], "liked": liked}
    finally:
        conn.close()

@router.post("/{id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(id: int, comment_in: CommentCreate, current_user: dict = Depends(get_current_user)):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM posts WHERE id = %s", (id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
            
            cur.execute(
                "INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s) RETURNING id, post_id, user_id, comment, created_at",
                (id, current_user["id"], comment_in.comment)
            )
            comment = cur.fetchone()
            conn.commit()
            return comment
    finally:
        conn.close()

@router.get("/{id}/comments", response_model=List[CommentResponse])
async def get_comments(id: int):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM comments WHERE post_id = %s ORDER BY created_at ASC", (id,))
            comments = cur.fetchall()
            return comments
    finally:
        conn.close()


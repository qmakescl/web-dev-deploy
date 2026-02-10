from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile, Form
from typing import List, Optional
from ..models import PostResponse
from ..database import db
from ..auth import get_current_user
from ..storage import storage_backend
import re

router = APIRouter()

def extract_tags(content: str) -> List[str]:
    return re.findall(r"#(\w+)", content)

@router.get("", response_model=List[PostResponse])
async def get_posts(current_user: Optional[dict] = Depends(get_current_user)):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            # 좋아요 수와 댓글 수를 포함한 게시글 조회
            query = """
                SELECT p.*, 
                    (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count,
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
            """
            if current_user:
                query += f", EXISTS(SELECT 1 FROM likes WHERE post_id = p.id AND user_id = {current_user['id']}) as is_liked "
            else:
                query += ", FALSE as is_liked "
            
            query += " FROM posts p ORDER BY p.created_at DESC"
            
            cur.execute(query)
            posts = cur.fetchall()
            return posts
    finally:
        conn.close()

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    content: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    img_url = await storage_backend.upload(file, file.filename)
    
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            # 1. 게시글 저장
            cur.execute(
                "INSERT INTO posts (user_id, img_url, content) VALUES (%s, %s, %s) RETURNING id, user_id, img_url, content, created_at, updated_at",
                (current_user["id"], img_url, content)
            )
            post = cur.fetchone()
            
            # 2. 태그 처리
            if content:
                tags = extract_tags(content)
                for tag_name in set(tags):
                    cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id", (tag_name,))
                    tag_id = cur.fetchone()["id"]
                    cur.execute("INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)", (post["id"], tag_id))
            
            conn.commit()
            return {**post, "like_count": 0, "comment_count": 0, "is_liked": False}
    except Exception as e:
        conn.rollback()
        await storage_backend.delete(img_url) # DB 실패 시 업로드된 파일 삭제
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/{id}", response_model=PostResponse)
async def get_post(id: int, current_user: Optional[dict] = Depends(get_current_user)):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT p.*, 
                    (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count,
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
            """
            if current_user:
                query += f", EXISTS(SELECT 1 FROM likes WHERE post_id = p.id AND user_id = {current_user['id']}) as is_liked "
            else:
                query += ", FALSE as is_liked "
            
            query += " FROM posts p WHERE p.id = %s"
            
            cur.execute(query, (id,))
            post = cur.fetchone()
            if not post:
                raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
            return post
    finally:
        conn.close()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)

async def delete_post(id: int, current_user: dict = Depends(get_current_user)):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, img_url FROM posts WHERE id = %s", (id,))
            post = cur.fetchone()
            if not post:
                raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
            if post["user_id"] != current_user["id"]:
                raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
            
            # 스토리지 파일 삭제
            if post["img_url"]:
                await storage_backend.delete(post["img_url"])
            
            cur.execute("DELETE FROM posts WHERE id = %s", (id,))
            conn.commit()
    finally:
        conn.close()

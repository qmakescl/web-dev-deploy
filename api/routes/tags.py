from fastapi import APIRouter, Depends
from typing import List, Optional
from ..models import PostResponse
from ..database import db
from ..auth import get_current_user

router = APIRouter()

@router.get("/{tag_name}", response_model=List[PostResponse])
async def get_posts_by_tag(tag_name: str, current_user: Optional[dict] = Depends(get_current_user)):
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
            
            query += """
                FROM posts p 
                JOIN post_tags pt ON p.id = pt.post_id
                JOIN tags t ON pt.tag_id = t.id
                WHERE t.name = %s
                ORDER BY p.created_at DESC
            """
            
            cur.execute(query, (tag_name,))
            posts = cur.fetchall()
            return posts
    finally:
        conn.close()

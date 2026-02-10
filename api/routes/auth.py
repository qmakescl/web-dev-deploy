from fastapi import APIRouter, HTTPException, status, Depends
from ..models import UserCreate, UserLogin, UserResponse, Token
from ..database import db
from ..auth import get_password_hash, verify_password, create_access_token
import psycopg2

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    conn = db.get_connection()
    try:
        hashed_password = get_password_hash(user_in.password)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
                (user_in.email, hashed_password)
            )
            user = cur.fetchone()
            conn.commit()
            return user
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일이 이미 존재합니다."
        )
    finally:
        conn.close()

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT email, password_hash FROM users WHERE email = %s", (user_in.email,))
            user = cur.fetchone()
            if not user or not verify_password(user_in.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="이메일 또는 비밀번호가 올바르지 않습니다."
                )
            
            access_token = create_access_token(data={"sub": user["email"]})
            return {"access_token": access_token, "token_type": "bearer"}
    finally:
        conn.close()

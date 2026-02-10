import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .database import db
from .config import settings
# 라우터 임포트
from .routes import auth, posts, interactions, tags

app = FastAPI(title="Insta-Lite API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 워크숍용으로 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # 애플리케이션 시작 시 DB 테이블 생성
    try:
        db.execute_ddl()
    except Exception as e:
        print(f"DB 연결 실패 (테이블 생성 건너뜀): {e}")

# 정적 파일 서빙 (로컬 개발용)
app.mount("/static", StaticFiles(directory="static"), name="static")
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(interactions.router, prefix="/api/posts", tags=["interactions"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])


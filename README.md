# 📸 Insta-Lite: 워크숍용 경량 인스타그램 클론

이 프로젝트는 웹 서비스의 핵심 요소인 **CRUD, 사용자 인증(Authentication), 데이터베이스 관계, 그리고 클라우드 배포**를 실습하기 위해 제작된 워크숍용 코드베이스입니다.

---

## 📑 목차
- [📸 Insta-Lite: 워크숍용 경량 인스타그램 클론](#-insta-lite-워크숍용-경량-인스타그램-클론)
  - [📑 목차](#-목차)
  - [🚀 주요 기능](#-주요-기능)
  - [🛠 기술 스택](#-기술-스택)
  - [💻 로컬 개발 설정](#-로컬-개발-설정)
  - [🌐 배포 가이드 (Vercel + Supabase)](#-배포-가이드-vercel--supabase)
  - [📁 프로젝트 구조](#-프로젝트-구조)
  - [📝 라이선스](#-라이선스)

---

## 🚀 주요 기능
- **인증 (Auth)**: JWT와 bcrypt를 이용한 회원가입 및 로그인 (비밀번호 안전 해싱 처리)
- **피드 (Feed)**: 이미지와 문구가 포함된 게시물 조회 (|#태그| 자동 인식)
- **상호작용 (Interactions)**: 게시물 좋아요(Like) 및 실시간 댓글(Comment) 작성
- **검색 (Search)**: 태그별 게시물 필터링 검색
- **반응형 UI**: 다크 모드 기반의 세련된 모바일 친화적 UI

## 🛠 기술 스택
- **Backend**: Python 3.12, FastAPI, Pydantic (Settings & Email validation)
- **Frontend**: Vanilla JS (ES6+), HTML5, CSS3 (CSS Variables & Flexbox)
- **Database**: PostgreSQL (Hosted on Supabase)
- **Storage**: Supabase Storage (Production) / Local Folder (Dev)
- **Infrastructure**: Vercel (Hosting), GitHub (Source Control)

## 💻 로컬 개발 설정

1. **저장소 클론 및 이동**
   ```bash
   git clone https://github.com/qmakescl/web-dev-deploy.git
   cd web-dev-deploy
   ```

2. **의존성 설치 (uv 권장)**
   ```bash
   uv sync
   source .venv/bin/activate
   ```

3. **환경 변수 설정 (.env)**
   `.env.example` 파일을 복사하여 `.env` 파일을 만들고 본인의 Supabase 정보를 입력합니다.
   ```bash
   DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres"
   SUPABASE_URL="https://[PROJECT-ID].supabase.co"
   SUPABASE_ANON_KEY="..."
   SUPABASE_SERVICE_ROLE_KEY="..."
   JWT_SECRET_KEY="your-random-secret-key"
   STORAGE_BACKEND="local" # 로컬 개발 시
   ```

4. **서버 실행**
   ```bash
   uv run uvicorn api.index:app --reload
   ```
   - 접속: `http://localhost:8000`

## 🌐 배포 가이드 (Vercel + Supabase)

1. **Supabase 준비**:
   - `Storage` 탭에서 버킷(예: `insta-lite`)을 생성하고 `Public`으로 설정합니다.
   - SQL Editor에서 테이블이 자동 생성되지 않을 경우 `api/database.py`의 DDL을 참조합니다.

2. **Vercel 설정**:
   - Vercel 대시보드에서 `New Project`로 GitHub 저장소를 연결합니다.
   - **Environment Variables**에 `.env`의 전역 변수들을 모두 입력합니다.
   - **중요**: `STORAGE_BACKEND`를 `supabase`로 설정해야 배포 환경에서 이미지가 정상 저장됩니다.

## 📁 프로젝트 구조
```text
.
├── api/                # FastAPI 백엔드 (Routes, Models, DB, Storage)
├── static/             # 프론트엔드 정적 파일 (HTML, CSS, JS)
├── instruction/        # 기획서(PRD) 및 가이드
├── vercel.json         # Vercel 배포 설정
├── requirements.txt    # 배포용 의존성 목록
└── pyproject.toml      # 로컬 패키지 관리 설정
```

---
📅 생성일: 2026-02-10 | Google Antigravity가 Q의 지침에 따라 생성함


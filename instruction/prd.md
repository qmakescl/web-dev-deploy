# [PRD] 경량 인스타그램 (Instagram Lite for Workshop) - 최종본
이 문서는 웹 서비스의 기본 구조인 **CRUD, 사용자 인증, 데이터베이스 관계**를 학습하기 위한 가이드라인입니다.

## 목차
- [1. 문서 개요](#1-문서-개요)
- [2. 사용자 스토리](#2-사용자-스토리-user-story)
- [3. 기능 명세](#3-기능-명세-feature-specifications)
- [4. 인터페이스 요구사항](#4-인터페이스-요구사항-uiux)
- [5. API 엔드포인트](#5-api-엔드포인트-restful)
- [6. 데이터베이스 설계](#6-데이터베이스-설계-erd)
- [7. 스토리지 아키텍처](#7-스토리지-아키텍처)
- [8. 배포 아키텍처](#8-배포-아키텍처)
- [9. 환경 변수 설정](#9-환경-변수-설정)
- [10. 에러 처리 범위](#10-에러-처리-범위)
- [11. 인수 조건](#11-인수-조건-definition-of-done)
- [12. 워크숍 진행 전략](#12-워크숍-진행-전략)

---

## 1. 문서 개요
- **프로젝트명**: 워크숍용 인스타 라이트 (Insta-Lite)
- **목표**: 3시간 내에 웹 서비스의 핵심 로직(회원가입, 게시글 작성, DB 저장)을 구현하고 배포함.
- **기술 스택**:

| 구분 | 기술 | 비고 |
|------|------|------|
| **Frontend** | HTML/CSS, Vanilla JS | 프레임워크 없이 순수 웹 기술 |
| **Backend** | Python 3.12 + FastAPI | 타입 힌트, 자동 API 문서 생성 |
| **Database** | PostgreSQL (Supabase) | 클라우드 매니지드 DB |
| **Storage** | Supabase Storage | 이미지 업로드용, 추상화 레이어 적용 |
| **Password Hashing** | bcrypt | 비밀번호 암호화 |
| **Package Manager** | uv | 빠르고 간편한 Python 패키지 관리 |
| **배포** | Vercel (Backend/Frontend) | 서버리스 배포 |
| **BaaS** | Supabase | DB + Storage + Auth 인프라 |

### 개발 환경 설정
프로젝트 루트에 `.venv` 가상환경을 `uv`로 설정합니다.

```bash
# 가상환경이 없는 경우 생성
if [ ! -d ".venv" ]; then
  uv init --python 3.12 && uv sync
fi

# 가상환경 활성화
source .venv/bin/activate

# 필요한 패키지 설치 (pyproject.toml에 정의된 의존성)
uv sync
```

### 환경 변수 파일 (.env)
프로젝트 루트에 `.env` 파일을 생성하여 Supabase 연결 정보를 관리합니다. **이 파일은 `.gitignore`에 반드시 포함**해야 합니다.

```env
# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database 설정 (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# JWT 설정
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Storage 설정
STORAGE_BACKEND=supabase
STORAGE_BUCKET_NAME=post-images
```

---

## 2. 사용자 스토리 (User Story)
입문자의 눈높이에서 사용자가 앱에서 경험할 시나리오입니다.

1. **가입**: "나는 소모임 활동을 위해 내 이메일로 계정을 만들고 싶어."
2. **게시**: "나는 내 일상을 담은 사진과 글을 올리고, 친구들이 검색하기 쉽게 `#태그`를 달고 싶어."
3. **교류**: "나는 친구의 글에 '좋아요'를 눌러 공감을 표시하고 싶어."
4. **관리**: "내가 올린 글에 오타가 있다면 수정하거나 삭제하고 싶어."

### 사용자 여정 (User Journey)

```mermaid
flowchart TD
    subgraph 인증
        A["🏠 랜딩 페이지"] --> B{"계정 있음?"}
        B -->|아니오| C["📝 회원가입"]
        C --> D["✉️ 이메일/비밀번호 입력"]
        D --> E["✅ 가입 완료"]
        E --> F["🔐 로그인"]
        B -->|예| F
        F --> G["🎫 토큰 발급"]
    end

    subgraph 메인활동
        G --> H["📰 피드 조회"]
        H --> I{"액션 선택"}
        I -->|글쓰기| J["📸 이미지 업로드"]
        J --> K["✍️ 본문 및 태그 작성"]
        K --> L["📤 게시물 업로드"]
        L --> H
        I -->|상세보기| M["📄 게시물 상세"]
        M --> N{"내 글?"}
        N -->|예| O["✏️ 수정 / 🗑️ 삭제"]
        O --> H
        N -->|아니오| P["❤️ 좋아요 / 💬 댓글"]
        P --> H
        I -->|검색| Q["🔍 태그 검색"]
        Q --> R["📋 필터링된 결과"]
        R --> H
    end

    subgraph 종료
        I -->|로그아웃| S["👋 로그아웃"]
        S --> A
    end
```

---

## 3. 기능 명세 (Feature Specifications)

### P0 (필수 기능: 이것이 없으면 서비스가 작동하지 않음)
- **F1. 이메일 기반 인증**:
  - **설명**: 사용자의 신원을 확인하는 과정입니다. DB에 `users` 테이블을 만들고 이메일과 `bcrypt`로 암호화된 비밀번호를 저장합니다.
  - **학습 포인트**: JWT 토큰을 통해 '로그인한 상태'를 유지하는 법을 배웁니다.
- **F2. 이미지 및 게시글 업로드**:
  - **설명**: 사진 파일을 서버로 보내면, 서버는 **스토리지 추상화 레이어**를 통해 Supabase Storage에 업로드한 뒤 그 **'공개 URL'**을 DB에 기록합니다.
  - **학습 포인트**: 클라이언트(브라우저)에서 서버로 파일을 전송하는 `Multipart/form-data` 개념과, 외부 스토리지 연동 방식을 이해합니다.
- **F3. 피드 조회 (Read)**:
  - **설명**: DB에 저장된 모든 게시물을 최신순으로 가져와 화면에 뿌려줍니다.
- **F4. 수정/삭제 권한 체크**:
  - **설명**: 수정/삭제 요청이 들어왔을 때 `현재 로그인한 유저 ID == 게시글 작성자 ID`인지 확인합니다.
  - **학습 포인트**: CRUD의 Update/Delete 완성 및 권한(Authorization) 개념 이해.

### P1 (보조 핵심 기능: 서비스의 재미를 더함)
- **F5. 좋아요 및 댓글**:
  - **설명**: 특정 게시물 ID와 사용자 ID를 연결하여 '좋아요' 테이블에 기록합니다.
  - **학습 포인트**: 데이터 간의 **1:N(게시글:댓글)** 또는 **N:M(사용자:좋아요)** 관계를 학습합니다.

### P2 (디테일 기능: 시간 여유 시 구현)
- **F6. 태그 검색**:
  - **설명**: 글 내용 중 `#` 뒤에 오는 단어를 추출해 `tags` 테이블에 저장하고, 검색 시 해당 태그가 연결된 게시물만 필터링합니다.
  - **학습 포인트**: N:M 관계(게시글:태그) 및 중간 테이블(`post_tags`) 개념 이해.

---

## 4. 인터페이스 요구사항 (UI/UX)
입문자용이므로 디자인보다는 **구조**에 집중합니다.

| 페이지 | 구성 요소 |
|--------|-----------|
| **회원가입 페이지** | 이메일, 비밀번호, 비밀번호 확인 입력란, 가입 버튼, 로그인 페이지 링크 |
| **로그인 페이지** | 이메일, 비밀번호 입력란, 로그인 버튼, 회원가입 페이지 링크 |
| **메인 피드 페이지** | 상단: 로고(홈 링크) + 로그아웃 버튼<br>글쓰기 버튼 (모달 혹은 별도 페이지)<br>카드 형태의 게시물 목록 (이미지 - 본문 - 태그 - 좋아요 버튼 - 댓글 리스트) |
| **게시글 상세 페이지** | 게시물 전체 내용, 댓글 작성 폼, 댓글 목록, 수정/삭제 버튼(작성자만 표시) |

---

## 5. API 엔드포인트 (RESTful)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| POST | `/api/auth/register` | 회원가입 | ❌ |
| POST | `/api/auth/login` | 로그인 (토큰 발급) | ❌ |
| GET | `/api/posts` | 전체 게시물 조회 | ❌ |
| POST | `/api/posts` | 게시물 작성 | ✅ |
| GET | `/api/posts/{id}` | 게시물 상세 조회 | ❌ |
| PUT | `/api/posts/{id}` | 게시물 수정 | ✅ (작성자만) |
| DELETE | `/api/posts/{id}` | 게시물 삭제 | ✅ (작성자만) |
| POST | `/api/posts/{id}/like` | 좋아요 토글 | ✅ |
| POST | `/api/posts/{id}/comments` | 댓글 작성 | ✅ |
| GET | `/api/tags/{tag_name}` | 태그별 게시물 검색 | ❌ |

---

## 6. 데이터베이스 설계 (ERD)
Supabase PostgreSQL에서 생성할 핵심 테이블 구조입니다.

> [!IMPORTANT]
> 초안 대비 주요 변경사항
> - SQLite → **PostgreSQL (Supabase)** 로 변경
> - 테이블/컬럼명을 PostgreSQL 컨벤션에 맞춰 **snake_case** 적용
> - `img_path` → `img_url`로 변경 (외부 스토리지 URL 저장)
> - `SERIAL` 타입 사용 (PostgreSQL 자동 증가)
> - `TIMESTAMP WITH TIME ZONE` 타입으로 시간대 지원

```mermaid
erDiagram
    users ||--o{ posts : writes
    users ||--o{ comments : writes
    users ||--o{ likes : gives
    posts ||--o{ comments : has
    posts ||--o{ likes : receives
    posts ||--o{ post_tags : has
    tags ||--o{ post_tags : belongs

    users {
        serial id PK
        varchar email UK
        varchar password_hash
        timestamptz created_at
    }
    posts {
        serial id PK
        int user_id FK
        varchar img_url
        text content
        timestamptz created_at
        timestamptz updated_at
    }
    comments {
        serial id PK
        int post_id FK
        int user_id FK
        text comment
        timestamptz created_at
    }
    likes {
        serial id PK
        int post_id FK
        int user_id FK
    }
    tags {
        serial id PK
        varchar name UK
    }
    post_tags {
        int post_id FK
        int tag_id FK
    }
```

### 테이블 요약

| 테이블 | 주요 필드 | 설명 |
|--------|-----------|------|
| **users** | id, email, password_hash, created_at | 사용자 정보 |
| **posts** | id, user_id, img_url, content, created_at, updated_at | 게시글 및 이미지 URL |
| **comments** | id, post_id, user_id, comment, created_at | 댓글 정보 |
| **likes** | id, post_id, user_id | 좋아요 (UNIQUE 제약: post_id + user_id) |
| **tags** | id, name | 태그 목록 |
| **post_tags** | post_id, tag_id | 게시글-태그 N:M 관계 (복합 PK) |

### PostgreSQL DDL

```sql
-- Users 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Posts 테이블
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    img_url VARCHAR(500),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments 테이블
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Likes 테이블 (중복 방지)
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(post_id, user_id)
);

-- Tags 테이블
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- PostTags 중간 테이블
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

-- 성능을 위한 인덱스
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_likes_post_id ON likes(post_id);
```

---

## 7. 스토리지 아키텍처
> [!IMPORTANT]
> 향후 AWS S3, Google Cloud Storage 등 다른 외부 스토리지로 교체할 수 있도록 **추상화 레이어**를 적용합니다.

### 스토리지 추상화 구조

```mermaid
classDiagram
    class StorageBackend {
        <<interface>>
        +upload(file, filename) str
        +delete(file_url) bool
        +get_public_url(filename) str
    }

    class SupabaseStorage {
        -supabase_client
        -bucket_name
        +upload(file, filename) str
        +delete(file_url) bool
        +get_public_url(filename) str
    }

    class LocalStorage {
        -upload_dir
        +upload(file, filename) str
        +delete(file_url) bool
        +get_public_url(filename) str
    }

    StorageBackend <|-- SupabaseStorage
    StorageBackend <|-- LocalStorage
```

- **`StorageBackend`** (인터페이스): 모든 스토리지 백엔드가 구현해야 하는 메서드 정의
- **`SupabaseStorage`** (운영용): Supabase Storage API를 통해 파일 업로드/삭제
- **`LocalStorage`** (개발용): 로컬 디렉토리에 파일 저장 (개발 시 Supabase 없이 테스트 가능)

### 업로드 흐름

```mermaid
sequenceDiagram
    participant Client as 클라이언트
    participant API as FastAPI 서버
    participant Storage as StorageBackend
    participant DB as PostgreSQL

    Client->>API: POST /api/posts (이미지 + 본문)
    API->>Storage: upload(file, unique_filename)
    Storage-->>API: 공개 URL 반환
    API->>DB: INSERT posts (img_url, content, ...)
    DB-->>API: 생성된 게시글 ID
    API-->>Client: 201 Created + 게시글 정보
```

### 환경별 스토리지 선택
`STORAGE_BACKEND` 환경 변수로 사용할 스토리지를 결정합니다:

| 환경 | STORAGE_BACKEND | 설명 |
|------|----------------|------|
| 로컬 개발 | `local` | `./uploads/` 디렉토리에 파일 저장 |
| 운영 (Vercel + Supabase) | `supabase` | Supabase Storage 버킷에 업로드 |

---

## 8. 배포 아키텍처

### 전체 아키텍처 다이어그램

```mermaid
flowchart LR
    subgraph Client["클라이언트"]
        Browser["🌐 웹 브라우저"]
    end

    subgraph Vercel["Vercel"]
        Frontend["📄 정적 파일\nHTML/CSS/JS"]
        Serverless["⚡ Serverless Functions\nFastAPI"]
    end

    subgraph Supabase["Supabase"]
        PostgreSQL["🐘 PostgreSQL\nDatabase"]
        SupaStorage["📦 Storage\n이미지 저장"]
    end

    Browser --> Frontend
    Browser --> Serverless
    Serverless --> PostgreSQL
    Serverless --> SupaStorage
    SupaStorage -.->|공개 URL| Browser
```

### 배포 구성 요소

| 구성 요소 | 플랫폼 | 역할 |
|-----------|--------|------|
| Frontend (HTML/CSS/JS) | Vercel | 정적 파일 서빙 |
| Backend (FastAPI) | Vercel Serverless Functions | API 엔드포인트 처리 |
| Database | Supabase PostgreSQL | 데이터 영속 저장 |
| File Storage | Supabase Storage | 이미지 파일 저장 및 CDN 제공 |

### Vercel 배포 설정 (`vercel.json`)

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "static/$1" }
  ]
}
```

### 프로젝트 디렉토리 구조 (배포 기준)

```
web-dev-deploy/
├── api/                       # Vercel Serverless Functions
│   ├── index.py               # FastAPI 앱 진입점
│   ├── database.py            # DB 연결 (asyncpg/SQLAlchemy)
│   ├── models.py              # Pydantic 모델
│   ├── auth.py                # JWT 인증 로직
│   └── storage/               # 스토리지 추상화 레이어
│       ├── __init__.py
│       ├── base.py            # StorageBackend 인터페이스
│       ├── supabase_storage.py
│       └── local_storage.py
├── static/                    # 정적 프론트엔드 파일
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── instruction/               # PRD 및 문서
│   ├── prd-draft.md
│   └── prd.md
├── .env                       # 환경 변수 (Git 미포함)
├── .env.example               # 환경 변수 템플릿
├── .gitignore
├── vercel.json                # Vercel 배포 설정
├── pyproject.toml             # Python 의존성
└── README.md
```

---

## 9. 환경 변수 설정

### `.env.example` (Git에 포함하여 팀원 공유용)

```env
# === Supabase 설정 ===
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# === Database 설정 (Supabase PostgreSQL) ===
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# === JWT 설정 ===
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# === Storage 설정 ===
# 'supabase' 또는 'local' 중 선택
STORAGE_BACKEND=supabase
STORAGE_BUCKET_NAME=post-images
```

### 환경 변수 설명

| 변수명 | 필수 | 설명 |
|--------|------|------|
| `SUPABASE_URL` | ✅ | Supabase 프로젝트 URL |
| `SUPABASE_ANON_KEY` | ✅ | Supabase 익명(공개) API 키 |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase 서비스 역할 키 (서버 전용) |
| `DATABASE_URL` | ✅ | PostgreSQL 연결 문자열 |
| `JWT_SECRET_KEY` | ✅ | JWT 토큰 서명용 비밀 키 |
| `JWT_ALGORITHM` | ❌ | JWT 알고리즘 (기본: HS256) |
| `JWT_EXPIRATION_MINUTES` | ❌ | 토큰 만료 시간 (기본: 60분) |
| `STORAGE_BACKEND` | ❌ | 스토리지 종류 (기본: supabase) |
| `STORAGE_BUCKET_NAME` | ❌ | Supabase Storage 버킷명 (기본: post-images) |

### Vercel 환경 변수 설정
Vercel 배포 시 **Vercel Dashboard > Settings > Environment Variables**에서 위 환경 변수를 등록합니다. Supabase와 Vercel의 통합(Integration)을 사용하면 자동으로 설정할 수도 있습니다.

---

## 10. 에러 처리 범위
워크숍 범위상 **최소한의 에러 핸들링**만 구현합니다.

| 상황 | 처리 방식 |
|------|-----------|
| 중복 이메일 가입 시도 | 400 Bad Request + "이미 존재하는 이메일입니다" |
| 잘못된 로그인 정보 | 401 Unauthorized + "이메일 또는 비밀번호가 틀립니다" |
| 권한 없는 수정/삭제 | 403 Forbidden + "권한이 없습니다" |
| 존재하지 않는 리소스 | 404 Not Found |
| 파일 업로드 실패 | 500 Internal Server Error + "파일 업로드에 실패했습니다" |
| DB 연결 실패 | 500 Internal Server Error + "서비스에 일시적인 문제가 있습니다" |
| 서버 내부 오류 | 500 Internal Server Error (상세 로그는 서버에만 기록) |

---

## 11. 인수 조건 (Definition of Done)
워크숍 종료 시 아래 항목이 통과되어야 성공입니다.

1. 새로운 이메일로 회원가입 후 로그인이 정상적으로 되는가?
2. 사진을 업로드했을 때, **Supabase Storage에 파일이 저장**되고 화면에 출력되는가?
3. 내가 작성한 글만 '수정/삭제' 버튼이 활성화(혹은 작동)되는가?
4. 좋아요 버튼을 누르면 즉시 반영되고, 다시 누르면 취소되는가?
5. 댓글을 작성하면 해당 게시물에 표시되는가?
6. (P2) 특정 태그를 검색했을 때 관련 게시물만 필터링되는가?
7. **가장 중요**: Vercel을 통해 외부 링크로 접속 가능하며, Supabase DB/Storage와 정상 연동되는가?

---

## 12. 워크숍 진행 전략

> **Boilerplate 제공 방식 권장**
>
> 3시간 워크숍이라면 코드를 처음부터 짜기보다, 아래 부분은 **미리 뼈대 코드**를 제공하고 핵심 로직을 직접 채워보게 하는 방식이 학습 효과가 가장 좋습니다.
>
> - 이미지 업로드 로직 (Supabase Storage 연동)
> - DB 연동 및 JWT 토큰 설정
> - 스토리지 추상화 레이어
> - 기본 HTML/CSS 템플릿
> - Vercel 배포 설정 (`vercel.json`)
>
> 참가자가 직접 구현할 부분:
> - IF문을 활용한 권한 체크 로직
> - CRUD API 핸들러 작성
> - 좋아요/댓글 기능 연결

### 초안 대비 주요 변경사항 요약

| 항목 | 초안 | 최종본 |
|------|------|--------|
| Database | SQLite (파일 기반) | PostgreSQL (Supabase 매니지드) |
| Storage | 로컬 서버 디렉토리 | Supabase Storage + 추상화 레이어 |
| 배포 플랫폼 | Render (예시) | Vercel (Serverless) |
| 환경 변수 | 없음 | `.env` 파일 + Vercel 환경 변수 |
| 이미지 경로 | `img_path` (로컬 경로) | `img_url` (공개 URL) |
| 테이블명 | PascalCase | snake_case (PostgreSQL 컨벤션) |
| 스토리지 확장성 | 없음 | 인터페이스 기반 추상화 (S3, GCS 교체 가능) |

---

> 📅 생성일: 2026-02-10 | Google Antigravity가 Q의 지침에 따라 생성함

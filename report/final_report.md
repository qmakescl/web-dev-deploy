# Insta-Lite 프로젝트 완료 보고서

## 목차
- [프로젝트 개요](#프로젝트-개요)
- [주요 작업 및 해결 내용](#주요-작업-및-해결-내용)
- [최종 기술 스택](#최종-기술-스택)
- [향후 유지보수 가이드](#향후-유지보수-가이드)

## 프로젝트 개요
Insta-Lite 프로젝트는 웹 서비스의 핵심 기능(CRUD, 인증, 파일 스토리지, 관계형 DB)을 학습하기 위한 워크숍용 애플리케이션으로 개발되었습니다. 로컬 환경에서의 디버깅을 거쳐 최종적으로 Vercel과 Supabase를 활용한 클라우드 배포까지 성공적으로 완료되었습니다.

## 주요 작업 및 해결 내용

### 1. 인증 및 보안 강화
- **Bcrypt 호환성 해결**: `passlib`과 최신 `bcrypt` 간의 72바이트 제한 오류를 해결하기 위해 `bcrypt`를 직접 호출하는 방식으로 로직을 교체하였습니다.
- **비밀번호 특수문자 처리**: 데이터베이스 연결 문자열(DATABASE_URL) 내 비밀번호의 특수문자(예: `%`, `#`)가 URL 인코딩 규칙을 따르도록 가이드하여 연결 오류를 해결하였습니다.

### 2. UI/UX 및 기능 보완
- **이미지 서빙 오류 수정**: 로컬 개발 시 `uploads` 디렉토리 마운트 설정을 추가하여 이미지가 깨지는 현상을 해결하였으며, 배포 환경에서의 유연성을 위해 디렉토리 존재 유무를 체크하는 로직을 추가했습니다.
- **댓글 및 검색 기능 구현**: 누락되었던 댓글 상세 보기 모달과 상단 태그 검색창을 추가하여 사용자 간 상호작용 기능을 강화했습니다.
- **백엔드 API 최적화**: 게시물 상세 정보 및 댓글 목록을 위한 전용 엔드포인트를 추가하여 프론트엔드 연동 완성도를 높였습니다.

### 3. 배포 및 소스 관리
- **Vercel 최적화**: 실행 시 발생하던 디렉토리 참조 오류를 수정하고, `requirements.txt`와 `vercel.json` 설정을 최적화했습니다.
- **GitHub 연동**: 최종 코드를 [GitHub 저장소](https://github.com/qmakescl/web-dev-deploy.git)에 푸시하고, 워크숍 참가자를 위한 상세 README 가이드를 작성했습니다.

## 최종 기술 스택

| Category | Technology |
| :--- | :--- |
| Framework | FastAPI (Python 3.12) |
| Frontend | Vanilla JavaScript, HTML5, CSS3 |
| Database | PostgreSQL (Supabase) |
| Storage | Supabase Storage / Local Storage |
| Authentication | JWT, Bcrypt |
| Hosting | Vercel |

## 향후 유지보수 가이드
- **스토리지 정책**: 현재 Supabase Storage의 버킷 정책이 Public으로 설정되어 있어야 이미지가 외부에서 정상적으로 보입니다.
- **환경 변수**: Vercel 대시보드에서 `STORAGE_BACKEND`를 `supabase`로 유지해야 하며, 시크릿 키 유출에 주의하십시오.

---
생성일: 2026-02-10
Google Antigravity가 Q의 지침에 따라 생성함

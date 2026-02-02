# FastAPI Boilerplate

FastAPI를 사용한 완전한 보일러플레이트 프로젝트입니다.

## 주요 기능

- 🔐 **인증 시스템**: JWT 기반 회원가입/로그인
- 👤 **사용자 관리**: 역할 기반 권한 관리 (Admin, Moderator, User)
- 📝 **게시판**: 게시글 CRUD, 댓글, 카테고리
- 📊 **대시보드**: 통계 및 최근 활동
- 🎨 **테마 설정**: 사용자별 테마 커스터마이징
- 📋 **동적 메뉴**: 역할 기반 메뉴 구조
- 🗄️ **다중 DB 지원**: PostgreSQL, MySQL, MariaDB, SQLite

## 빠른 시작

```bash
# 저장소 클론
git clone <repository-url>
cd FastAPI_Tutorial

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 서버 실행
uvicorn app.main:app --reload
```

## API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 자세한 문서

### 처음 시작하는 분들을 위한 가이드

- [웹 개발 입문 가이드](docs/00_introduction.md) - 웹, API, REST, HTTP 등 기초 개념
- [개발 환경 준비](docs/tutorial/00_before_you_start.md) - Python 설치, 터미널, VS Code, Git 기초

### 프로젝트 문서

- [설치 가이드](docs/01_installation.md)
- [환경 설정](docs/02_configuration.md)
- [사용 가이드](docs/03_usage.md)
- [API 레퍼런스](docs/04_api_reference.md)
- [수정 및 확장 가이드](docs/05_customization.md)

### FastAPI 튜토리얼

- [시작하기 전에](docs/tutorial/00_before_you_start.md) - 개발 환경 준비와 Python 기본기
- [FastAPI 기본](docs/tutorial/01_fastapi_basics.md) - 앱 생성, 라우트, 요청/응답, 의존성 주입
- [라우팅](docs/tutorial/02_routing.md)
- [데이터베이스](docs/tutorial/03_database.md)
- [인증](docs/tutorial/04_authentication.md)
- [CRUD 작업](docs/tutorial/05_crud.md)
- [테스트](docs/tutorial/06_testing.md)

## 프로젝트 구조

```
FastAPI_Tutorial/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 애플리케이션
│   ├── config.py         # 설정 관리
│   ├── database.py       # DB 연결
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   ├── routers/          # API 라우터
│   ├── services/         # 비즈니스 로직
│   ├── dependencies/     # 종속성 (인증 등)
│   └── utils/            # 유틸리티
├── tests/                # 테스트
├── docs/                 # 문서
├── alembic/              # DB 마이그레이션
├── requirements.txt
├── .env.example
└── README.md
```

## 라이선스

MIT License

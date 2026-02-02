# 환경 설정 가이드

이 문서에서는 프로젝트의 모든 설정 옵션을 설명합니다.

> **초보자 안내:** 환경 설정은 "서버에게 어떻게 동작할지 알려주는 것"입니다.
> 마치 핸드폰의 설정 앱에서 화면 밝기, 알림, Wi-Fi 등을 조절하는 것처럼,
> 서버도 DB 주소, 비밀 키, 토큰 유효기간 등을 설정해야 합니다.

## 목차

1. [환경 변수 개요](#환경-변수-개요)
2. [애플리케이션 설정](#애플리케이션-설정)
3. [데이터베이스 설정](#데이터베이스-설정)
4. [인증 설정](#인증-설정)
5. [CORS 설정](#cors-설정)
6. [테마 설정](#테마-설정)
7. [환경별 설정 관리](#환경별-설정-관리)

---

## 환경 변수 개요

### 환경 변수란?

프로그램이 실행될 때 필요한 **외부 설정값**입니다.

```
왜 코드에 직접 안 쓰나요?

❌ 나쁜 예 (코드에 직접 작성):
   DB_PASSWORD = "my_secret_password"    ← Git에 올라가면 비밀번호 노출!

✅ 좋은 예 (환경 변수 사용):
   DB_PASSWORD = os.getenv("DB_PASSWORD")  ← .env 파일에서 읽어옴
```

**장점:**
1. **보안**: 비밀번호 같은 민감한 정보를 코드에 노출하지 않음
2. **유연성**: 환경(개발/테스트/프로덕션)마다 다른 설정을 쉽게 적용
3. **편의성**: 코드 수정 없이 설정만 변경 가능

### 설정 파일 위치

```
FastAPI_Tutorial/
├── .env              # 실제 설정 (git에 포함되지 않음) ← 내 비밀번호가 여기에
├── .env.example      # 설정 템플릿 (git에 포함됨) ← 다른 사람이 참고하는 양식
└── app/
    └── config.py     # 설정 로드 및 검증 ← .env를 읽어오는 코드
```

### 설정 로드 방식

설정은 `app/config.py`의 `Settings` 클래스를 통해 로드됩니다:

```python
from app.config import settings

# 설정 사용 예시
print(settings.app_name)      # "FastAPI Boilerplate"
print(settings.database_url)  # "sqlite:///./data/app.db"
print(settings.debug)         # True
```

> **어떻게 동작하나요?**
> 1. 서버가 시작되면 `config.py`가 `.env` 파일을 읽음
> 2. 각 값을 `settings` 객체에 저장
> 3. 코드 어디에서든 `settings.xxx`로 설정값에 접근 가능

---

## 애플리케이션 설정

### 기본 설정

```env
# 애플리케이션 이름 (API 문서에 표시됨)
APP_NAME="FastAPI Boilerplate"

# 버전
APP_VERSION="1.0.0"

# 디버그 모드 (개발: true, 프로덕션: false)
DEBUG=true

# 비밀 키 (세션, CSRF 등에 사용)
# 프로덕션에서는 반드시 변경하세요!
SECRET_KEY="your-secret-key-change-this-in-production"
```

### 디버그 모드란?

| 기능 | DEBUG=true (개발 모드) | DEBUG=false (프로덕션 모드) |
|------|----------------------|--------------------------|
| SQL 로깅 | 활성화 (어떤 SQL이 실행되는지 보임) | 비활성화 |
| 상세 에러 | 에러 전체 내용 표시 (디버깅에 유용) | 간략한 메시지만 표시 (보안) |
| 핫 리로드 | 자동 (코드 수정 시 서버 재시작) | 수동 |

> **주의:** 프로덕션(실서비스)에서는 반드시 `DEBUG=false`로 설정하세요.
> 디버그 모드에서는 에러 시 서버 내부 정보가 노출될 수 있습니다.

### SECRET_KEY 생성

> **SECRET_KEY란?** 서버가 데이터를 암호화할 때 사용하는 비밀 문자열입니다.
> 은행 금고의 비밀번호와 같은 역할을 합니다.
> 이 값이 노출되면 토큰을 위조할 수 있으므로, 추측하기 어렵고 충분히 긴 값을 사용해야 합니다.

```python
# Python으로 안전한 키 생성
import secrets
print(secrets.token_urlsafe(32))
# 출력 예: 'dkG3h2bV7JKf9mN...' (매번 다른 값이 나옴)
```

또는 명령줄에서:

```bash
openssl rand -hex 32
```

---

## 데이터베이스 설정

### 데이터베이스 유형 선택

```env
# 지원 유형: postgresql, mysql, mariadb, sqlite
DB_TYPE=postgresql
```

### PostgreSQL 설정

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=fastapi_db
```

생성되는 URL: `postgresql://postgres:password@localhost:5432/fastapi_db`

> **이 URL의 구조:**
> ```
> postgresql://사용자:비밀번호@호스트:포트/데이터베이스이름
> ```

### MySQL/MariaDB 설정

```env
DB_TYPE=mysql  # 또는 mariadb
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=fastapi_db
```

생성되는 URL: `mysql+pymysql://root:password@localhost:3306/fastapi_db`

### SQLite 설정

```env
DB_TYPE=sqlite
SQLITE_FILE=./data/app.db
```

생성되는 URL: `sqlite:///./data/app.db`

> **SQLite는 왜 다른가요?** SQLite는 별도 서버 없이 파일 하나로 동작하므로,
> 호스트, 포트, 사용자, 비밀번호가 필요 없습니다. 파일 경로만 지정하면 됩니다.

### 연결 풀이란?

```python
# app/database.py에서 설정
engine = create_engine(
    database_url,
    pool_pre_ping=True,   # 연결 유효성 검사
    pool_size=10,         # 기본 연결 수
    max_overflow=20,      # 추가 연결 최대 수
)
```

> **연결 풀(Connection Pool)이란?**
> DB 연결을 매번 새로 만드는 대신, 미리 여러 개의 연결을 만들어놓고 재사용하는 것입니다.
>
> **비유:** 수영장의 레인처럼, 미리 10개의 연결 통로를 만들어놓고
> 요청이 올 때마다 빈 통로를 배정해주는 것입니다.
>
> - `pool_size=10`: 항상 준비해놓을 연결 수
> - `max_overflow=20`: 바쁠 때 추가로 만들 수 있는 연결 수
> - 즉, 최대 30개(10+20)의 동시 DB 연결이 가능

---

## 인증 설정

### JWT 설정

```env
# JWT 서명에 사용되는 비밀 키
# 프로덕션에서는 반드시 변경하세요!
JWT_SECRET_KEY="your-jwt-secret-key-change-this"

# 서명 알고리즘
JWT_ALGORITHM=HS256

# 액세스 토큰 만료 시간 (분)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 리프레시 토큰 만료 시간 (일)
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **각 설정의 의미:**
>
> - **JWT_SECRET_KEY**: JWT 토큰을 만들고 검증할 때 사용하는 비밀 키.
>   이 키가 노출되면 누구나 가짜 토큰을 만들 수 있으므로 절대 공유하지 마세요.
>
> - **JWT_ALGORITHM**: 암호화 방식. `HS256`은 가장 널리 사용되는 대칭 키 알고리즘입니다.
>   특별한 이유가 없으면 변경하지 않아도 됩니다.
>
> - **ACCESS_TOKEN_EXPIRE_MINUTES**: 로그인 후 발급받는 토큰의 유효 시간.
>   30분이 지나면 토큰이 만료되어 다시 인증이 필요합니다.
>
> - **REFRESH_TOKEN_EXPIRE_DAYS**: 액세스 토큰이 만료되었을 때 새 토큰을 받기 위한 토큰.
>   7일간 유효하므로, 7일 동안은 다시 로그인하지 않아도 됩니다.

### 토큰 만료 시간 권장값

| 환경 | 액세스 토큰 | 리프레시 토큰 | 설명 |
|------|-------------|---------------|------|
| 개발 | 60분 | 30일 | 자주 로그인하기 귀찮으므로 길게 |
| 프로덕션 | 15-30분 | 7일 | 보안과 편의성의 균형 |
| 고보안 | 5-15분 | 1일 | 은행, 의료 등 보안이 중요한 서비스 |

> **왜 액세스 토큰은 짧고, 리프레시 토큰은 길까요?**
>
> 택시 비유로 설명하면:
> - **액세스 토큰** = 택시 승차권 (짧은 유효기간, 자주 사용)
> - **리프레시 토큰** = 월정액 패스 (긴 유효기간, 승차권 재발급용)
>
> 승차권이 만료되면 월정액 패스로 새 승차권을 받습니다.
> 승차권을 누가 훔쳐도 30분만 쓸 수 있지만,
> 패스를 훔치면 오래 쓸 수 있으므로 패스는 더 안전하게 관리합니다.

### 사용자 역할

시스템에서 지원하는 역할:

```python
class UserRole(str, Enum):
    ADMIN = "admin"          # 전체 권한 (모든 것을 할 수 있음)
    MODERATOR = "moderator"  # 컨텐츠 관리 권한 (게시글/댓글 관리)
    USER = "user"            # 일반 사용자 (자기 글만 관리)
```

> **역할 기반 접근 제어(RBAC)란?**
> 사용자마다 "할 수 있는 것"을 역할로 구분하는 방식입니다.
>
> | 기능 | ADMIN | MODERATOR | USER |
> |------|-------|-----------|------|
> | 사용자 목록 조회 | O | X | X |
> | 다른 사용자 삭제 | O | X | X |
> | 다른 사람 게시글 삭제 | O | O | X |
> | 자기 게시글 작성/수정/삭제 | O | O | O |

---

## CORS 설정

### CORS란?

> **CORS(Cross-Origin Resource Sharing)**는 "다른 주소에서 오는 요청을 허용할지"에 대한 규칙입니다.
>
> 예를 들어:
> - 프론트엔드가 `http://localhost:3000`에서 실행되고
> - 백엔드 API가 `http://localhost:8000`에서 실행되면
> - 주소(origin)가 다르므로 브라우저가 기본적으로 요청을 차단합니다
> - CORS 설정으로 "localhost:3000에서 오는 요청은 허용해"라고 알려줘야 합니다

### 기본 설정

```env
# 허용된 오리진 (JSON 배열 형식)
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# 자격 증명 허용 (쿠키, Authorization 헤더 등)
CORS_ALLOW_CREDENTIALS=true

# 허용된 HTTP 메서드
CORS_ALLOW_METHODS=["*"]

# 허용된 헤더
CORS_ALLOW_HEADERS=["*"]
```

> **각 항목의 의미:**
> - `CORS_ORIGINS`: API를 호출할 수 있는 주소 목록 (프론트엔드 주소)
> - `CORS_ALLOW_CREDENTIALS`: 쿠키나 인증 헤더를 포함한 요청을 허용할지
> - `CORS_ALLOW_METHODS`: 허용할 HTTP 메서드 (`*` = 모두 허용)
> - `CORS_ALLOW_HEADERS`: 허용할 HTTP 헤더 (`*` = 모두 허용)

### 프로덕션 설정 예시

```env
# 특정 도메인만 허용
CORS_ORIGINS=["https://myapp.com","https://admin.myapp.com"]

# 특정 메서드만 허용
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE"]

# 특정 헤더만 허용
CORS_ALLOW_HEADERS=["Authorization","Content-Type"]
```

### CORS 관련 주의사항

1. **와일드카드(`*`) 사용 자제**: 프로덕션에서는 구체적인 도메인 지정
2. **자격 증명과 와일드카드**: `CORS_ALLOW_CREDENTIALS=true`일 때 오리진에 `*` 사용 불가
3. **프리플라이트 캐시**: 복잡한 요청의 경우 브라우저가 먼저 OPTIONS 요청을 보냄

> **CORS 에러가 나요!**
> 프론트엔드 개발 시 가장 흔한 에러입니다. 대부분 `CORS_ORIGINS`에
> 프론트엔드 주소를 추가하면 해결됩니다.
> ```env
> # 프론트엔드가 localhost:3000이라면:
> CORS_ORIGINS=["http://localhost:3000"]
> ```

---

## 테마 설정

### 테마 옵션

```env
# 기본 테마
DEFAULT_THEME=light

# 사용 가능한 테마 목록
AVAILABLE_THEMES=["light","dark","blue","green"]
```

### 테마 커스터마이징

사용자별 테마 설정은 `user_themes` 테이블에 저장됩니다:

```python
# UserTheme 모델 필드
{
    "theme_name": "dark",           # 테마 이름
    "sidebar_collapsed": false,     # 사이드바 상태
    "custom_settings": {            # 확장 설정 (JSON)
        "font_size": "medium",
        "language": "ko"
    }
}
```

---

## 설정 검증

설정이 올바르게 로드되었는지 확인하는 방법:

### 방법 1: Python 셸에서 확인

```bash
# 가상환경 활성화 후
python -c "from app.config import settings; print(f'DB: {settings.db_type}, Debug: {settings.debug}')"
```

### 방법 2: 서버 시작 시 로그 확인

서버를 시작하면 다음과 같은 로그가 표시됩니다:

```
FastAPI Boilerplate v1.0.0 시작...
데이터베이스: postgresql
디버그 모드: True
데이터베이스 테이블 생성 완료
```

---

## 환경별 설정 관리

> **왜 환경별로 설정을 분리하나요?**
> 개발할 때는 편의를 위해 SQLite를 쓰고, 실제 서비스에서는 PostgreSQL을 쓰는 것처럼,
> 환경마다 설정이 다를 수 있습니다. `.env` 파일을 환경별로 준비하면 됩니다.

### 개발 환경 (.env.development)

```env
DEBUG=true
DB_TYPE=sqlite
SQLITE_FILE=./data/dev.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 테스트 환경 (.env.test)

```env
DEBUG=true
DB_TYPE=sqlite
SQLITE_FILE=:memory:
```

> **`:memory:`란?** 파일 대신 메모리에 DB를 만드는 것입니다.
> 테스트가 끝나면 데이터가 사라지므로, 테스트마다 깨끗한 상태로 시작할 수 있습니다.

### 프로덕션 환경 (.env.production)

```env
DEBUG=false
DB_TYPE=postgresql
DB_HOST=production-db-host
SECRET_KEY=very-long-and-secure-key
JWT_SECRET_KEY=another-very-secure-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

---

## 다음 단계

- [사용 가이드](03_usage.md): API 사용 방법
- [API 레퍼런스](04_api_reference.md): 전체 API 문서

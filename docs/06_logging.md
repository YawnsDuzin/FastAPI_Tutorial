# 로깅 가이드

이 문서에서는 애플리케이션의 로깅 시스템 사용 방법을 설명합니다.

## 목차

1. [개요](#개요)
2. [로거 사용하기](#로거-사용하기)
3. [로그 레벨](#로그-레벨)
4. [요청/응답 로깅](#요청응답-로깅)
5. [파일 로깅](#파일-로깅)
6. [JSON 로깅](#json-로깅)
7. [커스터마이징](#커스터마이징)

---

## 개요

프로젝트는 Python의 표준 `logging` 모듈을 기반으로 한 로깅 시스템을 제공합니다.

### 주요 기능

- **콘솔 및 파일 로깅**: 동시 출력 지원
- **로그 로테이션**: `RotatingFileHandler`로 자동 파일 관리
- **JSON 포맷**: 로그 수집 시스템 연동 지원
- **요청/응답 로깅**: HTTP 요청 자동 로깅 미들웨어
- **환경별 설정**: 환경 변수로 로그 레벨 제어

### 파일 구조

```
app/
├── utils/
│   └── logger.py           # 로거 설정 모듈
└── middleware/
    ├── __init__.py
    └── logging.py          # 요청/응답 로깅 미들웨어
```

---

## 로거 사용하기

### 기본 사용법

```python
from app.utils.logger import get_logger

# 모듈별 로거 생성
logger = get_logger(__name__)

# 로그 출력
logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("심각한 에러")
```

### 라우터에서 사용

```python
from fastapi import APIRouter, HTTPException
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/users/{user_id}")
def get_user(user_id: int):
    logger.info(f"사용자 조회 요청: user_id={user_id}")

    user = user_service.get_user(user_id)
    if not user:
        logger.warning(f"사용자를 찾을 수 없음: user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.debug(f"사용자 조회 성공: {user.email}")
    return user
```

### 서비스에서 사용

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

class UserService:
    def create_user(self, data):
        logger.info(f"새 사용자 생성 시도: email={data.email}")

        try:
            user = User(**data.model_dump())
            self.db.add(user)
            self.db.commit()
            logger.info(f"사용자 생성 완료: id={user.id}")
            return user
        except Exception as e:
            logger.error(f"사용자 생성 실패: {str(e)}", exc_info=True)
            raise
```

### 예외 정보 포함

```python
try:
    result = risky_operation()
except Exception as e:
    # exc_info=True로 스택 트레이스 포함
    logger.error(f"작업 실패: {str(e)}", exc_info=True)
```

---

## 로그 레벨

### 레벨 종류

| 레벨 | 값 | 용도 |
|------|-----|------|
| DEBUG | 10 | 상세 디버깅 정보 |
| INFO | 20 | 일반 작동 정보 |
| WARNING | 30 | 잠재적 문제 경고 |
| ERROR | 40 | 에러 발생 |
| CRITICAL | 50 | 심각한 에러 |

### 환경별 권장 설정

```env
# 개발 환경
LOG_LEVEL=DEBUG

# 스테이징 환경
LOG_LEVEL=INFO

# 프로덕션 환경
LOG_LEVEL=WARNING
```

### 레벨 필터링

설정된 레벨 이상의 로그만 출력됩니다:

```python
# LOG_LEVEL=WARNING인 경우
logger.debug("출력 안됨")   # X
logger.info("출력 안됨")    # X
logger.warning("출력됨")    # O
logger.error("출력됨")      # O
```

---

## 요청/응답 로깅

### 자동 로깅

`LoggingMiddleware`가 모든 HTTP 요청을 자동으로 로깅합니다.

### 로그 포맷

```
# 요청 로그
[a1b2c3d4] --> GET /api/v1/users | Client: 127.0.0.1

# 응답 로그 (성공)
[a1b2c3d4] <-- GET /api/v1/users | Status: 200 | Time: 12.34ms

# 응답 로그 (클라이언트 에러)
[a1b2c3d4] <-- POST /api/v1/auth/login | Status: 401 | Time: 5.23ms

# 응답 로그 (서버 에러)
[a1b2c3d4] <-- GET /api/v1/posts/999 | Status: 500 | Time: 3.45ms
```

### 요청 ID 추적

모든 요청에 고유한 요청 ID가 부여되어 응답 헤더에 포함됩니다:

```
X-Request-ID: a1b2c3d4
X-Process-Time: 12.34ms
```

### 제외 경로

다음 경로는 로깅에서 자동 제외됩니다:

- `/health` - 헬스 체크
- `/metrics` - 메트릭
- `/favicon.ico` - 파비콘
- `/docs` - Swagger UI
- `/redoc` - ReDoc
- `/openapi.json` - OpenAPI 스펙

### 제외 경로 커스터마이징

`app/main.py`에서 설정:

```python
app.add_middleware(
    LoggingMiddleware,
    exclude_paths=[
        "/health",
        "/metrics",
        "/favicon.ico",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/internal/",  # 추가 경로
    ],
)
```

---

## 파일 로깅

### 활성화

```env
LOG_FILE_ENABLED=true
LOG_FILE_PATH=logs/app.log
```

### 로그 로테이션

파일이 지정된 크기에 도달하면 자동으로 백업됩니다:

```env
# 최대 파일 크기 (10MB)
LOG_FILE_MAX_BYTES=10485760

# 백업 파일 개수
LOG_FILE_BACKUP_COUNT=5
```

### 로테이션 동작

```
logs/
├── app.log        # 현재 로그 파일
├── app.log.1      # 가장 최근 백업
├── app.log.2      # 두 번째 백업
├── app.log.3      # 세 번째 백업
├── app.log.4      # 네 번째 백업
└── app.log.5      # 가장 오래된 백업 (다음 로테이션 시 삭제)
```

### 로그 파일 위치

기본 경로: `logs/app.log`

```env
# 커스텀 경로 설정
LOG_FILE_PATH=/var/log/myapp/application.log
```

---

## JSON 로깅

### 활성화

```env
LOG_JSON_FORMAT=true
```

### 출력 예시

```json
{
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "level": "INFO",
    "logger": "app.routers.users",
    "message": "사용자 조회 요청: user_id=1",
    "module": "users",
    "function": "get_user",
    "line": 25
}
```

### 예외 포함 시

```json
{
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "level": "ERROR",
    "logger": "app.services.user",
    "message": "사용자 생성 실패: duplicate key",
    "module": "user",
    "function": "create_user",
    "line": 42,
    "exception": "Traceback (most recent call last):\n  File ..."
}
```

### 로그 수집 시스템 연동

JSON 로깅은 다음 시스템과 쉽게 연동됩니다:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **AWS CloudWatch**
- **Datadog**

---

## 커스터마이징

### 로그 포맷 변경

```env
# 간단한 포맷
LOG_FORMAT="%(levelname)s - %(message)s"

# 상세 포맷 (기본값)
LOG_FORMAT="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

# 프로세스/스레드 정보 포함
LOG_FORMAT="%(asctime)s | %(levelname)s | %(process)d:%(thread)d | %(name)s | %(message)s"
```

### 날짜 포맷 변경

```env
# 기본값
LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S"

# ISO 형식
LOG_DATE_FORMAT="%Y-%m-%dT%H:%M:%S"

# 밀리초 포함
LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S.%f"
```

### 외부 라이브러리 로그 레벨 조정

`app/utils/logger.py`에서 설정:

```python
# SQLAlchemy SQL 로깅
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Uvicorn 로깅
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# httpx/httpcore (외부 HTTP 요청)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
```

### 커스텀 로거 생성

```python
from app.utils.logger import get_logger
import logging

# 특정 용도의 로거 생성
audit_logger = get_logger("audit")
audit_logger.setLevel(logging.INFO)

# 감사 로그 기록
audit_logger.info(f"사용자 로그인: user_id={user.id}, ip={client_ip}")
```

### 로그에 추가 컨텍스트 포함

```python
import logging

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, 'request_id', 'N/A')
        record.user_id = getattr(record, 'user_id', 'anonymous')
        return True

# 필터 적용
logger.addFilter(ContextFilter())
```

---

## 모범 사례

### 1. 적절한 로그 레벨 사용

```python
# Good
logger.debug("쿼리 파라미터: %s", params)  # 디버깅용 상세 정보
logger.info("사용자 생성 완료: id=%d", user.id)  # 주요 이벤트
logger.warning("API 호출 재시도: attempt=%d", retry_count)  # 잠재적 문제
logger.error("외부 API 호출 실패", exc_info=True)  # 에러

# Bad
logger.info("디버깅: x=%s, y=%s, z=%s", x, y, z)  # DEBUG 사용
logger.error("사용자가 없습니다")  # WARNING 또는 INFO 사용
```

### 2. 민감 정보 로깅 금지

```python
# Bad - 민감 정보 노출
logger.info(f"로그인 시도: email={email}, password={password}")

# Good - 민감 정보 마스킹
logger.info(f"로그인 시도: email={email}")
```

### 3. 구조화된 메시지 사용

```python
# Bad - 파싱하기 어려움
logger.info("User 123 created post 456")

# Good - 구조화된 정보
logger.info("게시글 생성 | user_id=%d | post_id=%d", user_id, post_id)
```

### 4. 예외 로깅 시 스택 트레이스 포함

```python
try:
    process_data()
except Exception as e:
    # exc_info=True로 전체 스택 트레이스 기록
    logger.error("데이터 처리 실패: %s", str(e), exc_info=True)
```

---

## 다음 단계

- [환경 설정](02_configuration.md): 로깅 환경 변수 상세
- [수정 및 확장](05_customization.md): 미들웨어 커스터마이징

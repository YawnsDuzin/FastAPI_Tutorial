# FastAPI 기본 문법

이 문서에서는 FastAPI의 기본 개념과 문법을 이 프로젝트 코드를 기반으로 설명합니다.

## 목차

1. [FastAPI 소개](#fastapi-소개)
2. [애플리케이션 생성](#애플리케이션-생성)
3. [라우트 정의](#라우트-정의)
4. [요청과 응답](#요청과-응답)
5. [Pydantic 모델](#pydantic-모델)
6. [의존성 주입](#의존성-주입)
7. [예외 처리](#예외-처리)

---

## FastAPI 소개

FastAPI는 Python으로 작성된 현대적인 웹 프레임워크입니다.

### 주요 특징

- **빠른 성능**: Starlette과 Pydantic 기반으로 Node.js, Go와 비슷한 성능
- **타입 힌트**: Python 타입 힌트를 활용한 자동 검증
- **자동 문서화**: Swagger UI와 ReDoc 자동 생성
- **비동기 지원**: async/await 네이티브 지원

### 이 프로젝트에서의 사용

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Boilerplate",
    description="API 설명",
    version="1.0.0"
)
```

---

## 애플리케이션 생성

### 기본 FastAPI 앱

```python
from fastapi import FastAPI

# FastAPI 인스턴스 생성
app = FastAPI()

# 가장 간단한 엔드포인트
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
```

### 프로젝트의 앱 구조

`app/main.py`에서 더 복잡한 구성을 사용합니다:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import api_router


# 수명 주기 관리 (시작/종료 이벤트)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    print("🚀 애플리케이션 시작...")
    init_db()  # DB 테이블 생성

    yield  # 앱 실행 중

    # 종료 시 실행
    print("👋 애플리케이션 종료...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",           # Swagger UI 경로
    redoc_url="/redoc",         # ReDoc 경로
    openapi_url="/openapi.json", # OpenAPI 스키마
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")
```

### 주요 매개변수

| 매개변수 | 설명 | 예시 |
|---------|------|------|
| `title` | API 제목 | "My API" |
| `description` | API 설명 | "This API does..." |
| `version` | API 버전 | "1.0.0" |
| `docs_url` | Swagger UI 경로 | "/docs" 또는 None |
| `redoc_url` | ReDoc 경로 | "/redoc" 또는 None |
| `openapi_url` | OpenAPI 스키마 경로 | "/openapi.json" |

---

## 라우트 정의

### HTTP 메서드

FastAPI는 모든 HTTP 메서드를 지원합니다:

```python
@app.get("/items")          # 조회
@app.post("/items")         # 생성
@app.put("/items/{id}")     # 전체 수정
@app.patch("/items/{id}")   # 부분 수정
@app.delete("/items/{id}")  # 삭제
```

### 프로젝트 예시 (app/routers/auth.py)

```python
from fastapi import APIRouter

router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,        # 응답 모델
    status_code=status.HTTP_201_CREATED, # HTTP 상태 코드
    summary="회원가입",                   # API 요약
    description="새로운 사용자 계정을 생성합니다."  # 상세 설명
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입 API

    이 docstring은 API 문서에 표시됩니다.
    """
    # 비즈니스 로직
    return user
```

### 경로 매개변수

```python
# 기본 경로 매개변수
@router.get("/users/{user_id}")
def get_user(user_id: int):  # 자동으로 int로 변환
    return {"user_id": user_id}

# 프로젝트 예시 (app/routers/posts.py)
@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,                    # 경로 매개변수
    db: Session = Depends(get_db)    # 의존성
):
    post = post_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post
```

### 쿼리 매개변수

```python
from fastapi import Query

# 기본 쿼리 매개변수
@router.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    # GET /items?skip=0&limit=10
    return {"skip": skip, "limit": limit}

# 프로젝트 예시 (app/routers/posts.py)
@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    category_id: Optional[int] = Query(None, description="카테고리 ID"),
    search: Optional[str] = Query(None, description="검색어"),
    db: Session = Depends(get_db)
):
    # 로직
    pass
```

### Query 매개변수 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `default` | 기본값 | `Query(10)` |
| `ge` | 최소값 (greater or equal) | `Query(1, ge=1)` |
| `le` | 최대값 (less or equal) | `Query(100, le=100)` |
| `min_length` | 문자열 최소 길이 | `Query(min_length=3)` |
| `max_length` | 문자열 최대 길이 | `Query(max_length=50)` |
| `regex` | 정규식 패턴 | `Query(regex="^[a-z]+$")` |
| `description` | 설명 (문서화) | `Query(description="검색어")` |

---

## 요청과 응답

### 요청 본문 (Request Body)

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float

@router.post("/items")
def create_item(item: ItemCreate):  # Pydantic 모델로 자동 검증
    return item
```

### 프로젝트 예시 (app/routers/posts.py)

```python
from app.schemas.post import PostCreate, PostResponse

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,                           # 요청 본문
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post_service = PostService(db)
    return post_service.create_post(post_data, current_user.id)
```

### 응답 모델

```python
from pydantic import BaseModel

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

    model_config = {"from_attributes": True}  # ORM 모드

@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    # SQLAlchemy 객체를 반환해도 자동으로 변환됨
    return db.query(Item).filter(Item.id == item_id).first()
```

### 여러 응답 상태

```python
from fastapi import HTTPException

@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    responses={
        404: {"description": "Item not found"},
        403: {"description": "Permission denied"}
    }
)
def get_item(item_id: int):
    item = get_item_from_db(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

---

## Pydantic 모델

Pydantic은 데이터 검증 및 직렬화를 담당합니다.

### 기본 모델

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
```

### 프로젝트 예시 (app/schemas/user.py)

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserCreate(BaseModel):
    """회원가입 스키마"""

    email: EmailStr = Field(
        ...,                              # 필수 필드
        description="사용자 이메일",
        example="user@example.com"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="사용자명"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="비밀번호"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """사용자명 검증"""
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("사용자명은 영문으로 시작해야 합니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 강도 검증"""
        if not re.search(r"[A-Z]", v):
            raise ValueError("대문자가 포함되어야 합니다.")
        if not re.search(r"\d", v):
            raise ValueError("숫자가 포함되어야 합니다.")
        return v
```

### 응답 스키마와 ORM 모드

```python
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    created_at: datetime

    # Pydantic v2 설정
    model_config = {
        "from_attributes": True,  # ORM 객체에서 변환 허용
        "json_schema_extra": {     # API 문서 예시
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "role": "user",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    }
```

### 상속을 통한 스키마 재사용

```python
# 기본 스키마
class PostBase(BaseModel):
    title: str
    content: str

# 생성용 (상속)
class PostCreate(PostBase):
    category_id: Optional[int] = None

# 수정용 (모든 필드 선택적)
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# 응답용 (상속 + 추가 필드)
class PostResponse(PostBase):
    id: int
    author: AuthorInfo
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

## 의존성 주입

FastAPI의 `Depends`는 강력한 의존성 주입 시스템입니다.

### 기본 의존성

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### 프로젝트의 인증 의존성 (app/dependencies/auth.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 스킴 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """현재 인증된 사용자 반환"""

    # 토큰 검증
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보를 확인할 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 조회
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """활성화된 사용자만 반환"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 계정입니다.")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """관리자만 반환"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    return current_user
```

### 의존성 사용

```python
# 인증 필요
@router.get("/profile")
def get_profile(user: User = Depends(get_current_active_user)):
    return user

# 관리자만
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin_user)
):
    # 관리자만 실행 가능
    pass

# 선택적 인증
@router.get("/posts")
def get_posts(
    user: Optional[User] = Depends(get_optional_current_user)
):
    # user가 None이면 비로그인 사용자
    pass
```

---

## 예외 처리

### HTTPException

```python
from fastapi import HTTPException, status

@router.get("/items/{item_id}")
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아이템을 찾을 수 없습니다."
        )
    return item
```

### 전역 예외 핸들러 (app/main.py)

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """검증 에러 핸들러"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "입력값 검증에 실패했습니다.",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 핸들러"""
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."}
    )
```

---

## 다음 단계

- [라우팅 심화](02_routing.md)
- [데이터베이스](03_database.md)
- [인증](04_authentication.md)

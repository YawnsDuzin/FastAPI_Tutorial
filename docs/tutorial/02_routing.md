# 라우팅 심화

이 문서에서는 FastAPI의 라우팅 시스템을 자세히 설명합니다.

## 목차

1. [APIRouter 사용](#apirouter-사용)
2. [라우터 구성](#라우터-구성)
3. [경로 매개변수](#경로-매개변수)
4. [쿼리 매개변수](#쿼리-매개변수)
5. [요청 본문](#요청-본문)
6. [응답 커스터마이징](#응답-커스터마이징)
7. [태그와 문서화](#태그와-문서화)

---

## APIRouter 사용

### APIRouter란?

`APIRouter`는 관련된 엔드포인트들을 그룹화하는 방법입니다.

### 기본 사용법

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_items():
    return []

@router.post("/")
def create_item():
    return {"created": True}
```

### 프로젝트 구조

```
app/routers/
├── __init__.py      # 라우터 통합
├── auth.py          # 인증 라우터
├── users.py         # 사용자 라우터
├── posts.py         # 게시글 라우터
├── dashboard.py     # 대시보드 라우터
├── theme.py         # 테마 라우터
└── menu.py          # 메뉴 라우터
```

---

## 라우터 구성

### 라우터 통합 (app/routers/__init__.py)

```python
from fastapi import APIRouter

from app.routers import auth, users, posts, dashboard, theme, menu

# 메인 API 라우터
api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(
    auth.router,
    prefix="/auth",       # URL 접두사
    tags=["인증"]          # API 문서 태그
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["사용자"]
)

api_router.include_router(
    posts.router,
    prefix="/posts",
    tags=["게시판"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["대시보드"]
)

api_router.include_router(
    theme.router,
    prefix="/theme",
    tags=["테마"]
)

api_router.include_router(
    menu.router,
    prefix="/menu",
    tags=["메뉴"]
)
```

### 메인 앱에 등록 (app/main.py)

```python
from app.routers import api_router

app = FastAPI()

# /api/v1 접두사로 모든 라우터 등록
app.include_router(api_router, prefix="/api/v1")
```

### 결과 URL 구조

```
/api/v1/auth/register     # 회원가입
/api/v1/auth/login        # 로그인
/api/v1/users/            # 사용자 목록
/api/v1/users/{id}        # 사용자 상세
/api/v1/posts/            # 게시글 목록
/api/v1/posts/{id}        # 게시글 상세
```

---

## 경로 매개변수

### 기본 사용

```python
@router.get("/users/{user_id}")
def get_user(user_id: int):
    # user_id는 자동으로 int로 변환됨
    return {"user_id": user_id}
```

### 타입별 변환

```python
# 정수
@router.get("/items/{item_id}")
def get_item(item_id: int):
    pass

# 문자열
@router.get("/files/{file_path:path}")  # :path는 슬래시 포함
def get_file(file_path: str):
    # /files/home/user/doc.txt → file_path = "home/user/doc.txt"
    pass

# UUID
from uuid import UUID

@router.get("/orders/{order_id}")
def get_order(order_id: UUID):
    pass
```

### 프로젝트 예시 (app/routers/posts.py)

```python
@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """게시글 상세 조회"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 미공개 글 권한 확인
    if not post.is_published:
        if not current_user or (
            post.author_id != current_user.id and
            not current_user.is_admin
        ):
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    post_service.increment_view_count(post_id)

    return post
```

### 경로 매개변수 검증

```python
from fastapi import Path

@router.get("/items/{item_id}")
def get_item(
    item_id: int = Path(
        ...,
        title="아이템 ID",
        description="조회할 아이템의 ID",
        ge=1,           # 최소값
        le=1000000,     # 최대값
        example=42
    )
):
    return {"item_id": item_id}
```

---

## 쿼리 매개변수

### 기본 사용

```python
@router.get("/items")
def get_items(
    skip: int = 0,      # 기본값 있음 = 선택적
    limit: int = 10
):
    # GET /items?skip=0&limit=10
    return {"skip": skip, "limit": limit}
```

### Query로 검증

```python
from fastapi import Query
from typing import Optional

@router.get("/search")
def search(
    q: str = Query(
        ...,                    # 필수
        min_length=1,
        max_length=100,
        description="검색어"
    ),
    category: Optional[str] = Query(
        None,                   # 선택적
        description="카테고리 필터"
    )
):
    return {"q": q, "category": category}
```

### 프로젝트 예시 (app/routers/posts.py)

```python
@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(
        1,
        ge=1,
        description="페이지 번호"
    ),
    size: int = Query(
        10,
        ge=1,
        le=50,
        description="페이지당 항목 수"
    ),
    category_id: Optional[int] = Query(
        None,
        description="카테고리 ID"
    ),
    search: Optional[str] = Query(
        None,
        description="검색어"
    ),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """게시글 목록 조회"""
    post_service = PostService(db)

    include_unpublished = current_user and current_user.is_admin

    posts, total = post_service.get_posts(
        page=page,
        size=size,
        category_id=category_id,
        search=search,
        include_unpublished=include_unpublished
    )

    return PostListResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0
    )
```

### 리스트 쿼리 매개변수

```python
from typing import List

@router.get("/items")
def get_items(
    tags: List[str] = Query(
        default=[],
        description="태그 필터"
    )
):
    # GET /items?tags=python&tags=fastapi
    return {"tags": tags}
```

---

## 요청 본문

### Pydantic 모델로 받기

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

@router.post("/items")
def create_item(item: ItemCreate):
    return item
```

### 프로젝트 예시 (app/routers/posts.py)

```python
from app.schemas.post import PostCreate, PostResponse

@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(
    post_data: PostCreate,                               # 요청 본문
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # 인증 필요
):
    """게시글 작성"""
    post_service = PostService(db)
    return post_service.create_post(post_data, current_user.id)
```

### 여러 본문 매개변수

```python
from fastapi import Body

@router.post("/items")
def create_item(
    item: ItemCreate,
    user_id: int = Body(...),  # 추가 본문 필드
    importance: int = Body(1, ge=1, le=5)
):
    # Request body:
    # {
    #     "item": {"name": "...", "price": ...},
    #     "user_id": 1,
    #     "importance": 3
    # }
    return {"item": item, "user_id": user_id}
```

### Form 데이터

```python
from fastapi import Form

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    # Content-Type: application/x-www-form-urlencoded
    return {"username": username}
```

### 프로젝트 예시 - OAuth2 로그인 (app/routers/auth.py)

```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """로그인 (OAuth2 표준 양식)"""
    auth_service = AuthService(db)
    return auth_service.login(form_data.username, form_data.password)
```

---

## 응답 커스터마이징

### response_model

```python
@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    # SQLAlchemy 모델을 반환해도 자동 변환
    return db.query(Item).get(item_id)
```

### 응답 필드 제외

```python
@router.get(
    "/users/me",
    response_model=UserResponse,
    response_model_exclude={"password", "secret_key"}
)
def get_me():
    return current_user
```

### 상태 코드

```python
from fastapi import status

@router.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    return item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    # 204 No Content - 본문 없이 반환
    pass
```

### 여러 응답 정의

```python
from fastapi.responses import JSONResponse

@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    responses={
        200: {"description": "성공", "model": ItemResponse},
        404: {"description": "찾을 수 없음"},
        500: {"description": "서버 오류"}
    }
)
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### 커스텀 응답

```python
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse

@router.get("/redirect")
def redirect():
    return RedirectResponse(url="/new-url")

@router.get("/file")
def get_file():
    return FileResponse("path/to/file.pdf")

@router.get("/custom")
def custom_response():
    return JSONResponse(
        content={"message": "Hello"},
        status_code=200,
        headers={"X-Custom-Header": "value"}
    )
```

---

## 태그와 문서화

### 라우터 태그

```python
router = APIRouter(
    prefix="/items",
    tags=["아이템"],
    responses={404: {"description": "Not found"}}
)
```

### 엔드포인트 문서화

```python
@router.post(
    "/",
    response_model=ItemResponse,
    summary="아이템 생성",
    description="새로운 아이템을 생성합니다.",
    response_description="생성된 아이템",
    deprecated=False,  # True면 deprecated 표시
    tags=["아이템"]
)
def create_item(item: ItemCreate):
    """
    아이템 생성 API

    - **name**: 아이템 이름 (필수)
    - **price**: 가격 (필수)
    - **description**: 설명 (선택)

    Returns:
        생성된 아이템 정보
    """
    return item
```

### 프로젝트 예시 (app/routers/auth.py)

```python
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다."
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입

    새로운 사용자 계정을 생성합니다.

    - **email**: 유효한 이메일 주소 (중복 불가)
    - **username**: 사용자명 (3-50자, 영문 시작, 중복 불가)
    - **password**: 비밀번호 (8자 이상, 대/소문자/숫자 포함)
    - **full_name**: 실제 이름 (선택)

    Returns:
        생성된 사용자 정보
    """
    user_service = UserService(db)
    return user_service.create_user(user_data)
```

---

## 다음 단계

- [데이터베이스](03_database.md)
- [인증](04_authentication.md)

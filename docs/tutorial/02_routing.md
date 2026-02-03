# 라우팅 심화

이 문서에서는 FastAPI의 라우팅 시스템을 자세히 설명합니다.

> **이 문서를 읽기 전에**: [FastAPI 기본 문법](01_fastapi_basics.md)을 먼저 읽으면 이해가 쉽습니다.

## 목차

1. [라우팅이란?](#라우팅이란)
2. [APIRouter 사용](#apirouter-사용)
3. [라우터 구성](#라우터-구성)
4. [경로 매개변수](#경로-매개변수)
5. [쿼리 매개변수](#쿼리-매개변수)
6. [요청 본문](#요청-본문)
7. [응답 커스터마이징](#응답-커스터마이징)
8. [태그와 문서화](#태그와-문서화)

---

## 라우팅이란?

> **초보자 안내:** 라우팅은 **"어떤 URL로 접근하면 어떤 코드를 실행할지"** 연결하는 것입니다.
>
> 택배 배송 시스템에 비유하면:
> ```
> [라우팅 = 택배 분류 시스템]
>
> 택배 도착 (HTTP 요청)
>     ↓
> ┌─────────────────────────────────────┐
> │         분류 센터 (라우터)           │
> │                                     │
> │  주소 확인 후 해당 배송팀으로 전달     │
> └─────────────────────────────────────┘
>     ↓              ↓              ↓
> 서울팀          부산팀          대전팀
> (/seoul)      (/busan)       (/daejeon)
> ```
>
> 웹에서는:
> ```
> 사용자 요청: GET /api/v1/posts/42
>     ↓
> 라우터가 경로 분석:
>   /api/v1  → API 버전 1
>   /posts   → 게시글 라우터로 전달
>   /42      → 42번 게시글
>     ↓
> posts.py의 get_post(42) 함수 실행
> ```

---

## APIRouter 사용

### APIRouter란?

`APIRouter`는 관련된 엔드포인트들을 그룹화하는 방법입니다.

> **초보자 안내:** `APIRouter`를 사용하면 코드를 **기능별로 파일을 나눌 수** 있습니다.
>
> 왜 파일을 나눌까요?
> ```python
> # ❌ 나쁜 예: main.py 하나에 모든 API를 작성
> # main.py가 수천 줄이 되면 유지보수가 어려워집니다
>
> @app.get("/users")
> @app.post("/users")
> @app.get("/posts")
> @app.post("/posts")
> @app.get("/comments")
> # ... 100개의 API가 한 파일에!
> ```
>
> ```python
> # ✅ 좋은 예: 기능별로 파일 분리
> # users.py → 사용자 관련 API만
> # posts.py → 게시글 관련 API만
> # comments.py → 댓글 관련 API만
> ```
>
> 회사 조직도에 비유하면:
> ```
> 대표이사 (main.py)
>     ├── 영업부 (auth.py) → 회원가입, 로그인
>     ├── 인사부 (users.py) → 사용자 관리
>     ├── 기획부 (posts.py) → 게시글 관리
>     └── 총무부 (dashboard.py) → 통계, 관리
> ```

### 기본 사용법

```python
from fastapi import APIRouter

# 1. 라우터 생성
router = APIRouter()

# 2. 라우터에 엔드포인트 등록 (app 대신 router 사용)
@router.get("/")
def get_items():
    return []

@router.post("/")
def create_item():
    return {"created": True}
```

> **코드 해석:**
> - `router = APIRouter()` → 새 라우터(그룹) 생성
> - `@router.get("/")` → `@app.get("/")` 대신 `@router.get("/")` 사용
> - 이 라우터를 나중에 main.py에서 `app.include_router()`로 등록합니다

### 프로젝트 구조

```
app/routers/
├── __init__.py      # 라우터 통합 (모든 라우터를 모아서 내보냄)
├── auth.py          # 인증 라우터 (회원가입, 로그인, 토큰 갱신)
├── users.py         # 사용자 라우터 (프로필, 사용자 관리)
├── posts.py         # 게시글 라우터 (게시글 CRUD, 댓글)
├── dashboard.py     # 대시보드 라우터 (통계, 최근 활동)
├── theme.py         # 테마 라우터 (사용자별 테마 설정)
└── menu.py          # 메뉴 라우터 (동적 메뉴 구조)
```

> **초보자 안내:** 파일 이름을 보면 어떤 기능인지 바로 알 수 있습니다.
> "로그인 관련 코드를 찾아야 해" → `auth.py` 열기!

---

## 라우터 구성

### 라우터 통합 (app/routers/__init__.py)

여러 라우터를 하나로 모으는 방법입니다:

```python
from fastapi import APIRouter

from app.routers import auth, users, posts, dashboard, theme, menu

# 메인 API 라우터 (모든 라우터를 모으는 역할)
api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(
    auth.router,
    prefix="/auth",       # URL 접두사: /auth/login, /auth/register
    tags=["인증"]          # Swagger UI에서 그룹 이름
)

api_router.include_router(
    users.router,
    prefix="/users",      # /users/, /users/{id}
    tags=["사용자"]
)

api_router.include_router(
    posts.router,
    prefix="/posts",      # /posts/, /posts/{id}
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

> **코드 해석:**
>
> | 매개변수 | 설명 | 예시 |
> |---------|------|------|
> | `auth.router` | 가져올 라우터 객체 | auth.py에서 정의한 router |
> | `prefix="/auth"` | URL 앞에 붙는 경로 | `/auth/login`, `/auth/register` |
> | `tags=["인증"]` | Swagger UI에서 그룹 이름 | API 목록에서 "인증" 섹션으로 표시 |

### 메인 앱에 등록 (app/main.py)

```python
from app.routers import api_router

app = FastAPI()

# /api/v1 접두사로 모든 라우터 등록
app.include_router(api_router, prefix="/api/v1")
```

> **초보자 안내:** `/api/v1`은 **API 버전**을 나타냅니다.
>
> 왜 버전을 붙이나요?
> ```
> 현재 버전: /api/v1/users    ← 기존 사용자들이 사용 중
> 새 버전:   /api/v2/users    ← 새로운 기능 추가, 기존 버전 유지
> ```
> 나중에 API를 크게 바꿀 때 기존 사용자에게 영향을 주지 않습니다.

### 결과 URL 구조

```
[전체 경로 구성]

app.include_router(prefix="/api/v1")
         ↓
    api_router.include_router(prefix="/auth")
                   ↓
              @router.post("/login")

최종 URL: /api/v1 + /auth + /login = /api/v1/auth/login
```

```
/api/v1/auth/register     # 회원가입
/api/v1/auth/login        # 로그인
/api/v1/auth/refresh      # 토큰 갱신
/api/v1/users/            # 사용자 목록
/api/v1/users/{id}        # 사용자 상세
/api/v1/users/me          # 내 정보
/api/v1/posts/            # 게시글 목록
/api/v1/posts/{id}        # 게시글 상세
/api/v1/posts/{id}/comments  # 게시글의 댓글
```

---

## 경로 매개변수

### 경로 매개변수란?

> **초보자 안내:** 경로 매개변수는 **URL 안에 변하는 값**을 넣는 방법입니다.
>
> ```
> /users/1     ← 1번 사용자
> /users/42    ← 42번 사용자
> /users/100   ← 100번 사용자
>        ↑
>    이 부분이 변합니다 (경로 매개변수)
> ```
>
> 코드에서는 `{변수명}` 형태로 표시합니다:
> ```python
> @router.get("/users/{user_id}")
> #                    ^^^^^^^^ 여기에 실제 값이 들어옴
> ```

### 기본 사용

```python
@router.get("/users/{user_id}")
def get_user(user_id: int):
    # /users/42 요청 → user_id = 42 (자동으로 int로 변환)
    return {"user_id": user_id}
```

> **초보자 안내:** `user_id: int`라고 타입을 지정하면:
>
> | 요청 URL | 결과 |
> |---------|------|
> | `/users/42` | ✅ user_id = 42 (정수로 변환) |
> | `/users/abc` | ❌ 422 에러 (정수가 아님) |
> | `/users/3.14` | ❌ 422 에러 (정수가 아님) |
>
> 타입 검증을 직접 작성할 필요가 없습니다!

### 타입별 변환

```python
# 정수
@router.get("/items/{item_id}")
def get_item(item_id: int):
    pass

# 문자열 (기본)
@router.get("/users/{username}")
def get_user(username: str):
    pass

# 경로 포함 문자열 (:path 사용)
@router.get("/files/{file_path:path}")  # :path는 슬래시(/)도 포함
def get_file(file_path: str):
    # /files/home/user/doc.txt → file_path = "home/user/doc.txt"
    pass

# UUID
from uuid import UUID

@router.get("/orders/{order_id}")
def get_order(order_id: UUID):
    # /orders/123e4567-e89b-12d3-a456-426614174000
    pass
```

> **초보자 안내:** `{file_path:path}`에서 `:path`는 특별한 의미입니다.
>
> 보통 URL에서 `/`는 경로 구분자입니다:
> ```
> /files/home/user/doc.txt
>        ↑    ↑    ↑
>       경로1 경로2 경로3  (3개로 나뉨)
> ```
>
> `:path`를 붙이면 `/`를 포함한 전체를 하나의 값으로 받습니다:
> ```
> file_path = "home/user/doc.txt"  (하나의 문자열)
> ```

### 프로젝트 예시 (app/routers/posts.py)

```python
@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,                                           # 경로 매개변수
    db: Session = Depends(get_db),                          # DB 연결
    current_user: Optional[User] = Depends(get_optional_current_user)  # 선택적 인증
):
    """게시글 상세 조회"""
    post_service = PostService(db)
    post = post_service.get_post(post_id)

    # 게시글이 없으면 404 에러
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 미공개 글은 작성자 또는 관리자만 볼 수 있음
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

> **코드 해석:**
>
> 1. `post_id: int` → URL에서 게시글 ID를 받음
> 2. `get_optional_current_user` → 로그인 안 해도 됨 (비로그인 시 None)
> 3. 미공개 글(`is_published=False`)은 작성자나 관리자만 볼 수 있음
> 4. 권한이 없으면 "404 찾을 수 없음"으로 응답 (보안을 위해 "권한 없음" 대신 "없음"으로)

### 경로 매개변수 검증

`Path`를 사용하면 더 세밀한 검증이 가능합니다:

```python
from fastapi import Path

@router.get("/items/{item_id}")
def get_item(
    item_id: int = Path(
        ...,                          # 필수 (기본값 없음)
        title="아이템 ID",             # Swagger 문서용 제목
        description="조회할 아이템의 ID",
        ge=1,                         # 최소값 (greater or equal: 1 이상)
        le=1000000,                   # 최대값 (less or equal: 100만 이하)
        example=42                    # Swagger 문서 예시
    )
):
    return {"item_id": item_id}
```

> **초보자 안내:** `Path` 옵션 정리
>
> | 옵션 | 의미 | 예시 |
> |------|------|------|
> | `ge=1` | 1 이상 (greater or equal) | 0이면 에러 |
> | `le=100` | 100 이하 (less or equal) | 101이면 에러 |
> | `gt=0` | 0 초과 (greater than) | 0이면 에러 |
> | `lt=100` | 100 미만 (less than) | 100이면 에러 |

---

## 쿼리 매개변수

### 쿼리 매개변수란?

> **초보자 안내:** 쿼리 매개변수는 **URL 뒤에 `?`로 시작하는 추가 정보**입니다.
>
> ```
> /posts?page=2&size=10&search=파이썬
>        ↑
>     ?부터가 쿼리 매개변수
> ```
>
> 각 부분의 의미:
> ```
> page=2      → 2페이지
> size=10     → 한 페이지에 10개
> search=파이썬 → "파이썬" 검색
> ```
>
> **경로 매개변수 vs 쿼리 매개변수:**
>
> | 구분 | 형태 | 용도 | 예시 |
> |------|------|------|------|
> | 경로 매개변수 | `/posts/{id}` | **무엇**을 조회할지 | `/posts/42` (42번 게시글) |
> | 쿼리 매개변수 | `/posts?key=val` | **어떻게** 조회할지 | `/posts?sort=latest` (최신순) |

### 기본 사용

```python
@router.get("/items")
def get_items(
    skip: int = 0,      # 기본값 0 = 선택적 (안 보내도 됨)
    limit: int = 10     # 기본값 10 = 선택적
):
    # GET /items              → skip=0, limit=10 (기본값 사용)
    # GET /items?skip=20      → skip=20, limit=10
    # GET /items?limit=5      → skip=0, limit=5
    # GET /items?skip=20&limit=5 → skip=20, limit=5
    return {"skip": skip, "limit": limit}
```

> **초보자 안내:** 기본값이 있으면 **선택적 매개변수**가 됩니다.
> ```python
> skip: int = 0    # 기본값 있음 → 선택적 (안 보내면 0)
> skip: int        # 기본값 없음 → 필수 (안 보내면 에러)
> ```

### Query로 검증

```python
from fastapi import Query
from typing import Optional

@router.get("/search")
def search(
    q: str = Query(
        ...,                    # 필수 (...)
        min_length=1,           # 최소 1글자
        max_length=100,         # 최대 100글자
        description="검색어"
    ),
    category: Optional[str] = Query(
        None,                   # 선택적 (기본값 None)
        description="카테고리 필터"
    )
):
    return {"q": q, "category": category}
```

> **코드 해석:**
>
> | 매개변수 | 설정 | 의미 |
> |---------|------|------|
> | `q` | `Query(...)` | 필수, 1~100자 |
> | `category` | `Query(None)` | 선택, 없으면 None |

### 프로젝트 예시 (app/routers/posts.py)

```python
@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(
        1,                      # 기본값: 1페이지
        ge=1,                   # 1 이상 (0페이지는 없음)
        description="페이지 번호"
    ),
    size: int = Query(
        10,                     # 기본값: 10개씩
        ge=1,                   # 최소 1개
        le=50,                  # 최대 50개 (서버 부담 방지)
        description="페이지당 항목 수"
    ),
    category_id: Optional[int] = Query(
        None,                   # 선택적
        description="카테고리 ID"
    ),
    search: Optional[str] = Query(
        None,                   # 선택적
        description="검색어"
    ),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """게시글 목록 조회"""
    post_service = PostService(db)

    # 관리자만 미공개 글 포함해서 볼 수 있음
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

> **초보자 안내:** 이 API 사용 예시:
>
> ```
> GET /posts                     → 1페이지, 10개 (기본값)
> GET /posts?page=2              → 2페이지, 10개
> GET /posts?size=20             → 1페이지, 20개
> GET /posts?search=파이썬        → "파이썬" 검색 결과
> GET /posts?category_id=3       → 3번 카테고리 게시글만
> GET /posts?page=2&size=5&search=FastAPI  → 조합 사용
> ```

### 리스트 쿼리 매개변수

같은 키로 여러 값을 받을 수 있습니다:

```python
from typing import List

@router.get("/items")
def get_items(
    tags: List[str] = Query(
        default=[],
        description="태그 필터"
    )
):
    # GET /items?tags=python&tags=fastapi&tags=web
    # → tags = ["python", "fastapi", "web"]
    return {"tags": tags}
```

> **초보자 안내:** 같은 이름을 여러 번 쓰면 리스트가 됩니다:
> ```
> ?tags=python&tags=fastapi
>    ↓
> tags = ["python", "fastapi"]
> ```

---

## 요청 본문

### 요청 본문이란?

> **초보자 안내:** 요청 본문(Request Body)은 **클라이언트가 서버에 보내는 데이터**입니다.
>
> 주로 POST, PUT, PATCH 요청에서 사용합니다.
>
> ```
> [회원가입 요청]
>
> POST /api/v1/auth/register
> Content-Type: application/json
>
> {                           ← 이 부분이 요청 본문
>   "email": "user@example.com",
>   "username": "newuser",
>   "password": "SecurePass123"
> }
> ```

### Pydantic 모델로 받기

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

@router.post("/items")
def create_item(item: ItemCreate):  # 요청 본문 → ItemCreate 객체
    return item
```

> **초보자 안내:** `item: ItemCreate`라고 쓰면 FastAPI가 자동으로:
> 1. 요청 본문의 JSON을 읽습니다
> 2. ItemCreate 형식에 맞는지 검증합니다
> 3. 맞으면 `item` 객체로 변환해서 전달합니다
> 4. 안 맞으면 422 에러를 반환합니다

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

> **코드 해석:**
> - `post_data: PostCreate` → 요청 본문을 PostCreate 스키마로 검증
> - `get_current_active_user` → 로그인한 사용자만 접근 가능
> - `status.HTTP_201_CREATED` → 성공 시 201 상태 코드 반환

### 여러 본문 매개변수

```python
from fastapi import Body

@router.post("/items")
def create_item(
    item: ItemCreate,
    user_id: int = Body(...),           # 추가 본문 필드
    importance: int = Body(1, ge=1, le=5)
):
    # 요청 본문:
    # {
    #     "item": {"name": "...", "price": ...},
    #     "user_id": 1,
    #     "importance": 3
    # }
    return {"item": item, "user_id": user_id}
```

### Form 데이터

HTML 폼에서 보내는 데이터를 받을 때 사용합니다:

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

> **초보자 안내:** Form과 Body(JSON)의 차이:
>
> | 형식 | Content-Type | 사용 예시 |
> |------|-------------|----------|
> | JSON (Body) | application/json | API 호출, 모바일 앱 |
> | Form | application/x-www-form-urlencoded | HTML 폼 전송, OAuth2 로그인 |

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

> **초보자 안내:** `OAuth2PasswordRequestForm`은 OAuth2 표준에 맞는 로그인 폼입니다.
> - `username`: 사용자명 또는 이메일
> - `password`: 비밀번호
>
> Swagger UI에서 "Authorize" 버튼을 누르면 이 형식으로 로그인됩니다.

---

## 응답 커스터마이징

### response_model

응답 데이터의 형식을 지정합니다:

```python
@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    # SQLAlchemy 모델을 반환해도 자동 변환
    return db.query(Item).get(item_id)
```

> **초보자 안내:** `response_model`의 역할:
>
> ```python
> # DB에서 가져온 데이터 (내부)
> Item(id=1, name="사과", price=1000, secret_code="ABC123", ...)
>
> # response_model=ItemResponse 적용 후 (외부로 보냄)
> {"id": 1, "name": "사과", "price": 1000}
> ```
>
> 불필요하거나 민감한 필드를 자동으로 제거합니다!

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

> **초보자 안내:** 자주 사용하는 상태 코드:
>
> | 코드 | 상수 | 의미 | 사용 시점 |
> |------|------|------|----------|
> | 200 | HTTP_200_OK | 성공 | 조회, 수정 성공 |
> | 201 | HTTP_201_CREATED | 생성됨 | 새 데이터 생성 |
> | 204 | HTTP_204_NO_CONTENT | 내용 없음 | 삭제 성공 |
> | 400 | HTTP_400_BAD_REQUEST | 잘못된 요청 | 클라이언트 오류 |
> | 404 | HTTP_404_NOT_FOUND | 찾을 수 없음 | 데이터 없음 |

### 여러 응답 정의

Swagger 문서에 가능한 응답들을 표시합니다:

```python
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

# 리다이렉트
@router.get("/redirect")
def redirect():
    return RedirectResponse(url="/new-url")

# 파일 다운로드
@router.get("/file")
def get_file():
    return FileResponse("path/to/file.pdf")

# 커스텀 헤더
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

### 태그란?

> **초보자 안내:** 태그는 Swagger UI에서 **API를 그룹으로 묶어서 보여주는** 기능입니다.
>
> ```
> [Swagger UI 화면]
>
> ▼ 인증                    ← 태그 (그룹 이름)
>   POST /api/v1/auth/register
>   POST /api/v1/auth/login
>
> ▼ 게시판                  ← 태그 (그룹 이름)
>   GET  /api/v1/posts/
>   POST /api/v1/posts/
>   GET  /api/v1/posts/{id}
> ```

### 라우터 태그

```python
router = APIRouter(
    prefix="/items",
    tags=["아이템"],                              # 이 라우터의 모든 API에 태그 적용
    responses={404: {"description": "Not found"}}  # 공통 응답 정의
)
```

### 엔드포인트 문서화

```python
@router.post(
    "/",
    response_model=ItemResponse,
    summary="아이템 생성",              # 짧은 설명 (목록에 표시)
    description="새로운 아이템을 생성합니다.",  # 상세 설명
    response_description="생성된 아이템",  # 응답 설명
    deprecated=False,                  # True면 deprecated 표시
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

> **초보자 안내:** 문서화 옵션:
>
> | 옵션 | 위치 | 용도 |
> |------|------|------|
> | `summary` | 데코레이터 | API 목록에 표시되는 짧은 설명 |
> | `description` | 데코레이터 | 상세 설명 |
> | docstring | 함수 본문 | Markdown 형식의 상세 설명 |
> | `deprecated=True` | 데코레이터 | "이 API는 곧 삭제됩니다" 표시 |

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

## 실수하기 쉬운 부분

> **초보자 안내:** 라우팅에서 자주 하는 실수들입니다:

### 1. 경로 순서 문제

```python
# ❌ 잘못된 순서
@router.get("/users/{user_id}")
def get_user(user_id: int): ...

@router.get("/users/me")      # 이 경로는 절대 실행되지 않음!
def get_me(): ...             # "me"가 user_id로 인식됨
```

```python
# ✅ 올바른 순서 (구체적인 경로를 먼저)
@router.get("/users/me")      # 먼저 정의
def get_me(): ...

@router.get("/users/{user_id}")  # 나중에 정의
def get_user(user_id: int): ...
```

### 2. 필수 vs 선택적 매개변수

```python
# ❌ 에러: 필수 매개변수 뒤에 기본값이 있는 매개변수
def get_items(skip: int, limit: int = 10):  # OK
def get_items(skip: int = 0, limit: int):   # 에러!
```

### 3. 경로 매개변수와 쿼리 매개변수 혼동

```python
# 경로 매개변수: URL 경로에 {변수}로 정의
@router.get("/users/{user_id}")
def get_user(user_id: int): ...  # /users/42

# 쿼리 매개변수: 함수 매개변수로만 정의
@router.get("/users")
def get_users(role: str): ...    # /users?role=admin
```

---

## 정리: 라우팅 흐름

```
[요청 흐름]

클라이언트 요청: GET /api/v1/posts/42?include_comments=true
                      ↓
┌─────────────────────────────────────────────────────┐
│ FastAPI 앱 (main.py)                                │
│   app.include_router(api_router, prefix="/api/v1") │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ API 라우터 (__init__.py)                            │
│   api_router.include_router(posts.router,          │
│                              prefix="/posts")       │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Posts 라우터 (posts.py)                             │
│   @router.get("/{post_id}")                        │
│   def get_post(post_id: int, ...):                 │
│       post_id = 42 (경로 매개변수)                   │
│       include_comments = True (쿼리 매개변수)        │
└─────────────────────────────────────────────────────┘
                      ↓
                   응답 반환
```

---

## 다음 단계

- [데이터베이스](03_database.md) - SQLAlchemy로 데이터 저장하기
- [인증](04_authentication.md) - JWT 인증 구현
- [FastAPI 기본](01_fastapi_basics.md) - 기본 개념 복습

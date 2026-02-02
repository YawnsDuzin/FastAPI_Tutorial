# FastAPI 기본 문법

이 문서에서는 FastAPI의 기본 개념과 문법을 이 프로젝트 코드를 기반으로 설명합니다.

> **이 문서를 읽기 전에**: [웹 개발 입문 가이드](../00_introduction.md)와 [개발 환경 준비](00_before_you_start.md)를 먼저 읽으면 이해가 쉽습니다.

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

> **초보자 안내:** "프레임워크"란 자주 필요한 기능들을 미리 만들어 둔 도구 모음입니다. 집을 지을 때 벽돌을 하나하나 굽는 대신, 미리 만들어진 건축 자재를 사용하는 것과 비슷합니다. FastAPI를 사용하면 웹 서버를 처음부터 만들 필요 없이, 정해진 규칙에 따라 코드를 작성하면 됩니다.

### 주요 특징

- **빠른 성능**: Starlette과 Pydantic 기반으로 Node.js, Go와 비슷한 성능
- **타입 힌트**: Python 타입 힌트를 활용한 자동 검증
- **자동 문서화**: Swagger UI와 ReDoc 자동 생성
- **비동기 지원**: async/await 네이티브 지원

> **초보자 안내:** 위 용어들이 낯설어도 괜찮습니다! 하나씩 풀어서 설명하겠습니다:
>
> | 특징 | 쉬운 설명 |
> |------|-----------|
> | **빠른 성능** | 같은 일을 시키면 다른 도구보다 빨리 처리합니다 |
> | **타입 힌트** | "이 값은 숫자여야 해"라고 미리 정해두면, FastAPI가 알아서 확인합니다 |
> | **자동 문서화** | API 사용 설명서를 자동으로 만들어 줍니다 (Swagger UI) |
> | **비동기 지원** | 여러 요청을 동시에 처리할 수 있습니다 (카페에서 주문 여러 개를 동시에 만드는 것처럼) |

### 왜 FastAPI를 선택할까?

다른 Python 웹 프레임워크와 비교해 보면:

| 비교 항목 | Flask | Django | FastAPI |
|----------|-------|--------|---------|
| 학습 난이도 | 쉬움 | 어려움 | 보통 |
| 성능 | 보통 | 보통 | 빠름 |
| 자동 문서화 | 없음 (별도 설치) | 없음 (별도 설치) | 내장 |
| 데이터 검증 | 수동 | 일부 자동 | 자동 |
| 비동기 지원 | 제한적 | 일부 지원 | 완전 지원 |

**결론**: FastAPI는 배우기 어렵지 않으면서도 성능이 좋고, 편의 기능이 많습니다.

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

> **코드 해석:**
> - `from fastapi import FastAPI` → FastAPI 라이브러리에서 `FastAPI` 클래스를 가져옵니다
> - `app = FastAPI(...)` → FastAPI 앱을 만듭니다. `app`이라는 이름은 관례입니다
> - `title`, `description`, `version` → Swagger UI 문서에 표시될 정보입니다

---

## 애플리케이션 생성

### 가장 간단한 FastAPI 앱

FastAPI로 만들 수 있는 가장 간단한 웹 서버입니다:

```python
from fastapi import FastAPI

# 1단계: FastAPI 인스턴스 생성
app = FastAPI()

# 2단계: 엔드포인트 정의
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
```

> **초보자 안내:** 이 코드가 하는 일을 단계별로 설명하면:
>
> 1. `app = FastAPI()` → 웹 서버를 만듭니다 (가게를 열었다고 생각하세요)
> 2. `@app.get("/")` → "누군가 홈페이지(`/`)에 접속하면" 이라는 뜻입니다
> 3. `def read_root():` → "이 함수를 실행해라" 라는 뜻입니다
> 4. `return {"message": "Hello, World!"}` → 이 데이터를 응답으로 보냅니다
>
> **`@app.get("/")`는 뭔가요?**
>
> `@`로 시작하는 것을 **데코레이터**라고 합니다. "이 함수를 특별한 용도로 등록해줘"라는 의미입니다.
> - `@app.get("/")` → GET 방식으로 "/" 경로에 접근하면 이 함수를 실행
> - `@app.post("/items")` → POST 방식으로 "/items" 경로에 접근하면 이 함수를 실행
>
> 비유하면, 식당에서 "1번 테이블 손님이 주문하면 → 이 레시피로 요리해라"라고 지정하는 것과 같습니다.

### 실행해 보기

위 코드를 `main.py`로 저장하고 실행하면:

```bash
uvicorn main:app --reload
```

브라우저에서 `http://localhost:8000`에 접속하면 다음과 같은 응답을 볼 수 있습니다:

```json
{"message": "Hello, World!"}
```

`http://localhost:8000/docs`에 접속하면 자동 생성된 API 문서를 볼 수 있습니다.

### 프로젝트의 앱 구조

실제 프로젝트(`app/main.py`)에서는 더 많은 기능을 설정합니다:

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
    print("애플리케이션 시작...")
    init_db()  # DB 테이블 생성

    yield  # 앱 실행 중

    # 종료 시 실행
    print("애플리케이션 종료...")


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

> **초보자 안내:** 코드가 길어 보이지만, 각 부분이 하는 일은 단순합니다:
>
> | 코드 부분 | 하는 일 | 비유 |
> |-----------|---------|------|
> | `lifespan` | 서버 시작/종료 시 할 일 정의 | 가게 오픈 준비 / 마감 정리 |
> | `FastAPI(...)` | 앱 생성 + 설정 | 가게 간판 달기 |
> | `add_middleware(CORS...)` | 다른 웹사이트에서 접근 허용 | "다른 동네 손님도 환영" 표시 |
> | `include_router(...)` | API 경로들을 등록 | 메뉴판 걸기 |
>
> **`yield`가 뭔가요?**
>
> `yield`는 "여기서 잠깐 멈추고, 나중에 다시 돌아와"라는 의미입니다.
> ```
> 서버 시작 → init_db() 실행 → yield(서버 가동 중...) → 서버 종료 시 yield 이후 코드 실행
> ```
> 쉽게 말해, `yield` 위쪽은 "가게 오픈 준비", 아래쪽은 "가게 마감 정리"입니다.

### 주요 매개변수

| 매개변수 | 설명 | 예시 |
|---------|------|------|
| `title` | API 제목 (문서에 표시) | "My API" |
| `description` | API 설명 (문서에 표시) | "This API does..." |
| `version` | API 버전 (문서에 표시) | "1.0.0" |
| `docs_url` | Swagger UI 경로 | "/docs" 또는 None(비활성화) |
| `redoc_url` | ReDoc 경로 | "/redoc" 또는 None(비활성화) |
| `openapi_url` | OpenAPI 스키마 경로 | "/openapi.json" |

---

## 라우트 정의

### 라우트(Route)란?

> **초보자 안내:** "라우트"는 **URL 경로와 처리 함수를 연결**하는 것입니다.
>
> 식당 비유로 설명하면:
> ```
> 손님: "비빔밥 주세요" (URL: /bibimbap)
>   → 주방에서 비빔밥 레시피 실행 (함수: make_bibimbap)
>
> 손님: "김치찌개 주세요" (URL: /kimchi-jjigae)
>   → 주방에서 김치찌개 레시피 실행 (함수: make_kimchi_jjigae)
> ```
>
> 웹에서는:
> ```
> 사용자: GET /users (사용자 목록 보여줘)
>   → get_users() 함수 실행
>
> 사용자: POST /users (새 사용자 만들어줘)
>   → create_user() 함수 실행
> ```

### HTTP 메서드

FastAPI는 모든 HTTP 메서드를 지원합니다:

```python
@app.get("/items")          # 조회 (데이터 가져오기)
@app.post("/items")         # 생성 (새 데이터 만들기)
@app.put("/items/{id}")     # 전체 수정 (데이터 통째로 바꾸기)
@app.patch("/items/{id}")   # 부분 수정 (일부만 바꾸기)
@app.delete("/items/{id}")  # 삭제 (데이터 지우기)
```

> **초보자 안내:** HTTP 메서드를 일상생활로 비유하면:
>
> | HTTP 메서드 | 비유 | 예시 |
> |------------|------|------|
> | `GET` | 메뉴판 보기 | 게시글 목록 조회 |
> | `POST` | 새 주문하기 | 새 게시글 작성 |
> | `PUT` | 주문 전체 변경 | 게시글 전체 수정 |
> | `PATCH` | 주문 일부 변경 | 게시글 제목만 수정 |
> | `DELETE` | 주문 취소 | 게시글 삭제 |
>
> **PUT vs PATCH 차이:**
> - `PUT`: 데이터를 **통째로** 교체합니다 (빠진 필드는 기본값으로)
> - `PATCH`: **변경한 부분만** 업데이트합니다

### APIRouter - 라우트 그룹 만들기

실제 프로젝트에서는 `@app.get()` 대신 `APIRouter`를 사용합니다:

```python
# 왜 APIRouter를 사용하나요?
# app.get()으로 모든 라우트를 main.py에 쓰면 파일이 너무 길어집니다.
# APIRouter로 기능별로 파일을 나눌 수 있습니다.

# 비유: 회사의 부서별 전화번호 체계
# - 영업부: 1000번대 (auth 라우터: /api/v1/auth/...)
# - 인사부: 2000번대 (users 라우터: /api/v1/users/...)
# - 기획부: 3000번대 (posts 라우터: /api/v1/posts/...)
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

> **코드 해석:**
>
> ```python
> @router.post("/register", ...)
> ```
> - `router.post` → POST 요청을 처리합니다
> - `"/register"` → `/register` 경로에 연결합니다
> - `response_model=UserResponse` → 응답 데이터의 형태를 지정합니다 (불필요한 필드 자동 제거)
> - `status_code=status.HTTP_201_CREATED` → 성공 시 201 상태 코드를 보냅니다 (201 = "새로 만들었습니다")
>
> ```python
> def register(user_data: UserCreate, db: Session = Depends(get_db)):
> ```
> - `user_data: UserCreate` → 요청 본문(body)을 `UserCreate` 형식으로 받습니다
> - `db: Session = Depends(get_db)` → 데이터베이스 연결을 자동으로 받습니다 (의존성 주입, 아래에서 자세히 설명)

### 경로 매개변수 (Path Parameters)

URL에 변하는 값을 넣을 수 있습니다:

```python
# 기본 경로 매개변수
@router.get("/users/{user_id}")
def get_user(user_id: int):  # 자동으로 int로 변환 및 검증
    return {"user_id": user_id}
```

> **초보자 안내:** `{user_id}`는 **"여기에 실제 값이 들어온다"**는 표시입니다.
>
> ```
> GET /users/1    → user_id = 1
> GET /users/42   → user_id = 42
> GET /users/abc  → 오류! (int가 아니므로 자동으로 422 에러 반환)
> ```
>
> `user_id: int`라고 타입을 지정하면, FastAPI가 자동으로:
> 1. 문자열 "42"를 숫자 42로 변환합니다
> 2. 숫자가 아닌 값("abc")이 오면 에러 메시지를 반환합니다
>
> **직접 변환 코드를 쓸 필요가 없습니다!**

### 프로젝트 예시 (app/routers/posts.py)

```python
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

### 쿼리 매개변수 (Query Parameters)

URL 뒤에 `?key=value` 형태로 추가 조건을 전달합니다:

```python
from fastapi import Query

# 기본 쿼리 매개변수
@router.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    # GET /items?skip=0&limit=10
    return {"skip": skip, "limit": limit}
```

> **초보자 안내:** 쿼리 매개변수는 **"필터"나 "옵션"**을 전달할 때 사용합니다.
>
> ```
> URL: /items?skip=0&limit=10
>          ↑         ↑
>     0개 건너뛰고   10개만 가져와
>
> 비유: "책 목록 보여줘. 처음부터(skip=0) 10권만(limit=10)"
> ```
>
> **경로 매개변수 vs 쿼리 매개변수:**
> ```
> /users/42           ← 경로 매개변수: 특정 리소스를 지정 (42번 사용자)
> /users?role=admin   ← 쿼리 매개변수: 필터/옵션 (관리자인 사용자들)
> ```
>
> - 경로 매개변수: **"무엇을"** 찾을지 (필수)
> - 쿼리 매개변수: **"어떻게"** 찾을지 (선택)

### 프로젝트 예시 (app/routers/posts.py)

```python
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

> **코드 해석:**
>
> ```python
> page: int = Query(1, ge=1, description="페이지 번호")
> ```
> - `page: int` → `page` 매개변수는 정수 타입
> - `Query(1, ...)` → 기본값은 1 (값을 안 보내면 1로 설정)
> - `ge=1` → "greater than or equal to 1" → 1 이상이어야 함 (0이나 음수 불가)
> - `description="페이지 번호"` → Swagger UI 문서에 표시되는 설명
>
> ```python
> category_id: Optional[int] = Query(None, ...)
> ```
> - `Optional[int]` → 정수이거나 없을 수 있음 (선택 사항)
> - `Query(None)` → 기본값은 None (안 보내도 됨)

### Query 매개변수 옵션 정리

| 옵션 | 설명 | 예시 |
|------|------|------|
| `default` | 기본값 | `Query(10)` |
| `ge` | 최소값 (greater or equal) | `Query(1, ge=1)` → 1 이상 |
| `le` | 최대값 (less or equal) | `Query(100, le=100)` → 100 이하 |
| `gt` | 초과 (greater than) | `Query(gt=0)` → 0보다 큼 |
| `lt` | 미만 (less than) | `Query(lt=100)` → 100 미만 |
| `min_length` | 문자열 최소 길이 | `Query(min_length=3)` |
| `max_length` | 문자열 최대 길이 | `Query(max_length=50)` |
| `regex` | 정규식 패턴 | `Query(regex="^[a-z]+$")` |
| `description` | 설명 (문서화) | `Query(description="검색어")` |

---

## 요청과 응답

### 전체 흐름 이해하기

> **초보자 안내:** API 요청-응답의 전체 흐름을 이해해 봅시다:
>
> ```
> [클라이언트]                              [서버 (FastAPI)]
>     |                                         |
>     |  POST /api/v1/posts                     |
>     |  Body: {"title": "안녕", "content": "..."}  |
>     | ──────────────────────────────────────→ |
>     |                                         |
>     |         1. URL 경로 확인                  |
>     |         2. 요청 데이터 검증 (Pydantic)     |
>     |         3. 함수 실행 (비즈니스 로직)        |
>     |         4. 응답 데이터 생성                |
>     |                                         |
>     |  201 Created                            |
>     |  {"id": 1, "title": "안녕", ...}         |
>     | ←────────────────────────────────────── |
> ```
>
> FastAPI가 자동으로 해주는 것:
> - 요청 데이터를 Python 객체로 변환
> - 데이터 형식 검증 (타입이 맞는지, 필수 값이 있는지)
> - Python 객체를 JSON으로 변환하여 응답

### 요청 본문 (Request Body)

클라이언트가 서버에 데이터를 보낼 때 사용합니다:

```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float

@router.post("/items")
def create_item(item: ItemCreate):  # Pydantic 모델로 자동 검증
    return item
```

> **초보자 안내:**
>
> `item: ItemCreate`라고 쓰면, FastAPI가 자동으로:
> 1. 요청 본문(body)의 JSON을 읽습니다
> 2. `ItemCreate` 형식에 맞는지 확인합니다
> 3. 맞으면 → `item` 변수에 담아서 함수에 전달
> 4. 안 맞으면 → 자동으로 422 에러 응답 (어떤 필드가 잘못됐는지 알려줌)
>
> ```json
> // 올바른 요청
> {"name": "사과", "price": 1000}     ← OK!
>
> // 잘못된 요청
> {"name": "사과"}                    ← 에러! price가 없음
> {"name": "사과", "price": "비싸"}   ← 에러! price는 숫자여야 함
> ```

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

> **코드 해석:**
> - `post_data: PostCreate` → 요청 본문을 `PostCreate` 형식으로 받음
> - `response_model=PostResponse` → 응답을 `PostResponse` 형식으로 변환
> - `current_user: User = Depends(...)` → 로그인한 사용자 정보를 자동으로 가져옴
>
> **`PostCreate`와 `PostResponse`가 다른 이유:**
> ```
> PostCreate (입력용):  title, content, category_id
> PostResponse (출력용): id, title, content, author, created_at, ...
> ```
> 입력할 때는 `id`나 `created_at`이 필요 없고(서버가 만드므로), 출력할 때는 `password` 같은 민감한 정보는 빼야 합니다.

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

> **초보자 안내:** `response_model`의 역할:
>
> ```python
> # DB에서 가져온 데이터 (내부)
> {id: 1, name: "사과", price: 1000, secret_code: "ABC", internal_note: "메모"}
>
> # response_model=ItemResponse 적용 후 (외부로 보내는 데이터)
> {id: 1, name: "사과", price: 1000}
> ```
>
> `response_model`은 **"응답에 이 필드들만 포함해"**라는 필터 역할을 합니다.
> 민감한 데이터(비밀번호, 내부 메모 등)가 실수로 노출되는 것을 방지합니다.
>
> **`model_config = {"from_attributes": True}`란?**
>
> SQLAlchemy 모델(DB 객체)을 Pydantic 모델(응답 객체)로 자동 변환하려면 이 설정이 필요합니다.
> 쉽게 말해, "DB에서 가져온 객체를 JSON으로 바꿀 수 있게 해줘"라는 설정입니다.

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

> **초보자 안내:** `responses`는 Swagger UI 문서에 "이런 에러도 발생할 수 있다"고 표시하는 역할입니다. 실제 동작에는 영향을 주지 않고, 문서화 목적입니다.

---

## Pydantic 모델

### Pydantic이란?

> **초보자 안내:** Pydantic은 **"데이터가 올바른 형식인지 자동으로 검사해주는 도구"**입니다.
>
> 비유하면 공항 보안 검색대와 같습니다:
> ```
> [승객의 짐]                    [보안 검색대 (Pydantic)]
>                                     |
> 여권 (str) ───────────────→ ✅ 문자열 맞음
> 나이 (int) ───────────────→ ✅ 숫자 맞음
> 이메일 (email) ───────────→ ✅ 이메일 형식 맞음
> 비밀번호 (str, 8자 이상) ──→ ❌ 5자밖에 안 됨! → 422 에러
> ```
>
> **왜 필요한가요?**
>
> 검증 없이 데이터를 받으면:
> ```python
> # 위험한 코드 (검증 없음)
> def create_user(data):
>     name = data["name"]     # name이 없으면? → 서버 에러!
>     age = data["age"]       # age가 문자열이면? → 나중에 에러!
>     email = data["email"]   # 이메일 형식이 아니면? → 잘못된 데이터 저장!
> ```
>
> Pydantic을 사용하면 이런 문제를 **자동으로** 잡아줍니다.

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

> **코드 해석:**
>
> | 코드 | 의미 |
> |------|------|
> | `email: EmailStr` | email 필드는 이메일 형식이어야 함 |
> | `username: str = Field(...)` | username은 필수(`...`) 문자열 |
> | `min_length=3, max_length=50` | 3~50자 사이여야 함 |
> | `full_name: Optional[str] = None` | full_name은 선택 사항, 안 보내면 None |
>
> **`...`(Ellipsis)란?**
>
> Python에서 `...`은 "여기에 값이 반드시 들어와야 한다"는 의미로 사용됩니다.
> `Field(...)`는 "이 필드는 필수입니다"라는 뜻입니다.

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

> **초보자 안내:** `@field_validator`는 **커스텀 검증 규칙**을 추가하는 기능입니다.
>
> Pydantic이 기본으로 해주는 검증(타입, 길이 등) 외에 추가 규칙이 필요할 때 사용합니다.
>
> ```
> 기본 검증 (자동):
>   - email이 이메일 형식인지
>   - username이 3~50자 문자열인지
>   - password가 8자 이상인지
>
> 커스텀 검증 (@field_validator):
>   - username이 영문으로 시작하는지
>   - password에 대문자와 숫자가 포함되어 있는지
> ```
>
> **검증 순서:**
> 1. 기본 타입 검증 (str, int, EmailStr 등)
> 2. Field 옵션 검증 (min_length, max_length 등)
> 3. @field_validator 검증 (커스텀 규칙)

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
# 기본 스키마 (공통 필드)
class PostBase(BaseModel):
    title: str
    content: str

# 생성용 (PostBase를 상속 + 추가 필드)
class PostCreate(PostBase):
    category_id: Optional[int] = None

# 수정용 (모든 필드 선택적)
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# 응답용 (PostBase를 상속 + 서버가 만드는 필드)
class PostResponse(PostBase):
    id: int
    author: AuthorInfo
    created_at: datetime

    model_config = {"from_attributes": True}
```

> **초보자 안내:** 왜 스키마를 여러 개 만들까요?
>
> ```
> 같은 "게시글"이지만 상황마다 필요한 필드가 다릅니다:
>
> [게시글 작성 시 (PostCreate)]     [게시글 조회 시 (PostResponse)]
> ┌─────────────────────┐        ┌──────────────────────────┐
> │ title: "제목"        │        │ id: 1                    │
> │ content: "내용"      │        │ title: "제목"             │
> │ category_id: 1      │        │ content: "내용"           │
> └─────────────────────┘        │ author: {name: "홍길동"}   │
>   ↑ id는 서버가 만들어요         │ created_at: "2024-01-01"  │
>   ↑ author는 로그인 정보에서      └──────────────────────────┘
>   ↑ created_at은 현재 시간으로      ↑ 사용자에게 보여줄 정보
> ```
>
> **상속(`PostBase`)의 장점:**
> - `title`과 `content`를 매번 반복해서 쓰지 않아도 됩니다
> - 공통 필드를 한 곳에서 관리할 수 있습니다

---

## 의존성 주입

### 의존성 주입(Dependency Injection)이란?

> **초보자 안내:** "의존성 주입"이라는 이름이 어렵지만, 개념은 단순합니다.
>
> **"함수가 필요한 것을 자동으로 준비해주는 시스템"**입니다.
>
> 비유: 레스토랑 주방
> ```
> [셰프가 직접 다 하는 경우 (의존성 주입 없음)]
> 1. 냉장고에서 재료 꺼내기       ← 셰프가 직접
> 2. 재료 손질하기               ← 셰프가 직접
> 3. 요리하기                   ← 셰프가 직접
>
> [보조 셰프가 있는 경우 (의존성 주입)]
> 1. 재료가 손질되어 도착         ← 보조 셰프가 준비 (자동)
> 2. 요리하기                   ← 셰프는 요리만 집중!
> ```
>
> FastAPI에서는:
> ```python
> # 의존성 주입 없이 (직접 다 하기)
> @router.get("/items")
> def get_items():
>     db = SessionLocal()        # DB 연결 직접 만들기
>     try:
>         items = db.query(Item).all()
>         return items
>     finally:
>         db.close()             # DB 연결 직접 닫기
>
> # 의존성 주입 사용 (자동으로 준비)
> @router.get("/items")
> def get_items(db: Session = Depends(get_db)):  # DB가 자동으로 준비됨!
>     return db.query(Item).all()                # 핵심 로직만 작성
> ```

### 기본 의존성: 데이터베이스 연결

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db      # db를 함수에 전달
    finally:
        db.close()    # 함수 실행 후 자동으로 연결 닫기

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

> **초보자 안내:** `Depends(get_db)`의 동작 순서:
>
> ```
> 1. 요청 들어옴
> 2. FastAPI가 get_db() 실행 → DB 연결 생성
> 3. yield db → db를 get_items 함수에 전달
> 4. get_items 함수 실행
> 5. 함수 끝남 → finally 블록 실행 → db.close()
> ```
>
> **핵심 포인트:** DB 연결/해제를 매번 직접 쓰지 않아도 됩니다!

### 프로젝트의 인증 의존성 (app/dependencies/auth.py)

이 프로젝트에서는 의존성 주입을 인증에도 활용합니다:

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

> **초보자 안내:** 의존성이 **체인(사슬)**처럼 연결됩니다:
>
> ```
> get_current_admin_user
>    ↓ Depends
> get_current_active_user
>    ↓ Depends
> get_current_user
>    ↓ Depends          ↓ Depends
> oauth2_scheme       get_db
> (토큰 추출)          (DB 연결)
> ```
>
> **실행 순서:**
> 1. 요청의 `Authorization` 헤더에서 토큰 추출 (`oauth2_scheme`)
> 2. DB 연결 생성 (`get_db`)
> 3. 토큰을 검증하고 사용자 조회 (`get_current_user`)
> 4. 사용자가 활성 상태인지 확인 (`get_current_active_user`)
> 5. 사용자가 관리자인지 확인 (`get_current_admin_user`)
>
> 이 모든 과정이 `Depends(get_current_admin_user)` 한 줄로 실행됩니다!

### 의존성 사용

```python
# 로그인한 사용자만 접근 가능
@router.get("/profile")
def get_profile(user: User = Depends(get_current_active_user)):
    return user

# 관리자만 접근 가능
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin_user)
):
    # 관리자만 실행 가능
    pass

# 로그인 안 해도 접근 가능 (로그인하면 추가 정보 제공)
@router.get("/posts")
def get_posts(
    user: Optional[User] = Depends(get_optional_current_user)
):
    # user가 None이면 비로그인 사용자
    pass
```

> **초보자 안내:** 의존성을 사용하면 **접근 권한을 한 줄로 설정**할 수 있습니다:
>
> | 의존성 | 누가 접근할 수 있나 |
> |--------|---------------------|
> | `Depends(get_current_active_user)` | 로그인한 활성 사용자 |
> | `Depends(get_current_admin_user)` | 관리자만 |
> | `Depends(get_optional_current_user)` | 누구나 (로그인 선택) |
> | 의존성 없음 | 누구나 (인증 불필요) |

---

## 예외 처리

### 예외 처리란?

> **초보자 안내:** 예외 처리는 **"문제가 생겼을 때 어떻게 대응할지"** 정하는 것입니다.
>
> ```
> 예외 처리가 없으면:
>   사용자: "999번 게시글 보여줘"
>   서버: 💥 크래시! (500 Internal Server Error)
>   사용자: "뭐가 잘못된 거지...?"
>
> 예외 처리가 있으면:
>   사용자: "999번 게시글 보여줘"
>   서버: "404 - 게시글을 찾을 수 없습니다."
>   사용자: "아, 없는 게시글이구나!"
> ```

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

> **코드 해석:**
>
> ```python
> raise HTTPException(status_code=404, detail="메시지")
> ```
> - `raise` → 에러를 **발생**시킵니다 (함수 실행이 여기서 멈춤)
> - `HTTPException` → HTTP 에러 응답을 보내는 특별한 에러
> - `status_code=404` → "찾을 수 없음" (HTTP 상태 코드)
> - `detail="메시지"` → 사용자에게 보여줄 에러 메시지
>
> **자주 사용하는 상태 코드:**
>
> | 코드 | 상수 | 의미 |
> |------|------|------|
> | 400 | `HTTP_400_BAD_REQUEST` | 잘못된 요청 |
> | 401 | `HTTP_401_UNAUTHORIZED` | 인증 필요 (로그인 안 됨) |
> | 403 | `HTTP_403_FORBIDDEN` | 권한 없음 (로그인은 했지만 권한 부족) |
> | 404 | `HTTP_404_NOT_FOUND` | 찾을 수 없음 |
> | 409 | `HTTP_409_CONFLICT` | 충돌 (이미 존재하는 데이터) |
> | 422 | `HTTP_422_UNPROCESSABLE_ENTITY` | 검증 실패 (데이터 형식 오류) |

### 전역 예외 핸들러 (app/main.py)

개별 함수가 아니라 앱 전체에서 특정 에러를 처리하는 방법입니다:

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

> **초보자 안내:** 전역 예외 핸들러는 **"모든 API에 공통으로 적용되는 에러 처리"**입니다.
>
> ```
> 개별 예외 처리:                   전역 예외 핸들러:
> ┌──────────┐                    ┌──────────────────────┐
> │ API 1    │ → 404 처리          │ 모든 API에서 발생하는   │
> │ API 2    │ → 404 처리          │ 검증 에러를 한 곳에서   │
> │ API 3    │ → 404 처리          │ 통일된 형식으로 처리    │
> └──────────┘                    └──────────────────────┘
>   ↑ 각자 따로 처리                 ↑ 한 번만 정의하면 전체 적용
> ```
>
> - `validation_exception_handler`: Pydantic 검증 에러를 보기 좋은 형식으로 바꿔줍니다
> - `global_exception_handler`: 예상치 못한 에러가 발생해도 서버가 죽지 않고 정중한 에러 메시지를 보냅니다

---

## 정리: FastAPI 코드를 읽는 순서

프로젝트 코드를 처음 볼 때 이 순서로 읽으면 이해하기 쉽습니다:

```
1. app/main.py         → 앱이 어떻게 시작되는지
2. app/routers/        → 어떤 API가 있는지 (URL 경로들)
3. app/schemas/        → 어떤 데이터를 주고받는지 (입력/출력 형식)
4. app/services/       → 실제 비즈니스 로직이 어떻게 동작하는지
5. app/models/         → 데이터베이스에 어떻게 저장되는지
6. app/dependencies/   → 인증 등 공통 기능이 어떻게 작동하는지
```

> **팁:** Swagger UI(`http://localhost:8000/docs`)에서 API 목록을 먼저 보고, 궁금한 API의 라우터 코드를 찾아보는 것이 가장 효율적입니다.

---

## 다음 단계

- [라우팅 심화](02_routing.md) - 라우터 구성과 미들웨어
- [데이터베이스](03_database.md) - SQLAlchemy ORM 사용법
- [인증](04_authentication.md) - JWT 인증 구현

# CRUD 작업

이 문서에서는 FastAPI에서 완전한 CRUD(Create, Read, Update, Delete) 작업을 구현하는 방법을 설명합니다.

> **이 문서를 읽기 전에**: [데이터베이스](03_database.md)와 [인증](04_authentication.md)을 먼저 읽으면 이해가 쉽습니다.

## CRUD란?

> **초보자 안내:** CRUD는 데이터를 다루는 **4가지 기본 작업**의 약자입니다.
>
> ```
> [CRUD = 데이터의 생애 주기]
>
> C - Create (생성)  : 새 데이터를 만든다    → 게시글 작성
> R - Read (조회)    : 데이터를 읽는다       → 게시글 보기
> U - Update (수정)  : 데이터를 바꾼다       → 게시글 수정
> D - Delete (삭제)  : 데이터를 지운다       → 게시글 삭제
>
> [HTTP 메서드와 매핑]
>
> ┌──────────┬────────────┬───────────────────┐
> │   CRUD   │ HTTP 메서드 │      예시 URL      │
> ├──────────┼────────────┼───────────────────┤
> │ Create   │ POST       │ POST /posts       │
> │ Read     │ GET        │ GET /posts/1      │
> │ Update   │ PUT/PATCH  │ PUT /posts/1      │
> │ Delete   │ DELETE     │ DELETE /posts/1   │
> └──────────┴────────────┴───────────────────┘
> ```
>
> **거의 모든 웹 서비스가 CRUD로 이루어져 있습니다:**
> - 쇼핑몰: 상품 등록(C), 상품 조회(R), 가격 수정(U), 상품 삭제(D)
> - SNS: 글 작성(C), 타임라인 보기(R), 글 수정(U), 글 삭제(D)
> - 메모장: 메모 작성(C), 메모 보기(R), 메모 수정(U), 메모 삭제(D)

## 목차

1. [CRUD 패턴 개요](#crud-패턴-개요)
2. [서비스 레이어](#서비스-레이어)
3. [Create (생성)](#create-생성)
4. [Read (조회)](#read-조회)
5. [Update (수정)](#update-수정)
6. [Delete (삭제)](#delete-삭제)
7. [페이지네이션](#페이지네이션)

---

## CRUD 패턴 개요

### 아키텍처

> **초보자 안내:** 코드를 계층(Layer)으로 나누면 관리가 쉬워집니다.
>
> ```
> [레스토랑 비유]
>
> 손님(Client) → 웨이터(Router) → 주방장(Service) → 냉장고(Database)
>
> 손님: "파스타 주세요"
> 웨이터: 주문을 받아서 주방에 전달
> 주방장: 요리 로직 수행 (삶고, 볶고, 담기)
> 냉장고: 재료 저장소
>
> [코드 구조]
>
> 클라이언트 → Router (요청 받기) → Service (로직 처리) → Model (DB 저장)
>             │                    │                    │
>             │ "POST /posts"      │ "게시글 생성"       │ "INSERT INTO..."
>             │ 입력 검증           │ 비즈니스 규칙       │ SQL 실행
>             │ 응답 형식           │ 에러 처리          │
> ```

```
Router (API 엔드포인트)
    ↓
Service (비즈니스 로직)
    ↓
Model (데이터베이스)
```

### 이점

| 장점 | 설명 | 예시 |
|------|------|------|
| **관심사 분리** | 각 레이어가 명확한 책임 | Router는 HTTP만, Service는 로직만 |
| **테스트 용이성** | 서비스 로직을 독립적으로 테스트 | DB 없이도 로직 테스트 가능 |
| **재사용성** | 서비스 로직을 여러 라우터에서 재사용 | 웹/모바일 API에서 같은 Service 사용 |
| **유지보수성** | 로직 변경 시 해당 레이어만 수정 | DB 바꿔도 Router는 수정 불필요 |

---

## 서비스 레이어

> **초보자 안내:** 서비스 레이어는 **"비즈니스 로직 담당 클래스"**입니다.
>
> ```
> [왜 서비스 레이어를 사용하나요?]
>
> ❌ 서비스 없이:
> @router.post("/posts")
> def create_post(data: PostCreate, db: Session):
>     # 50줄의 복잡한 로직이 여기에...
>     # 다른 곳에서 재사용 불가
>
> ✅ 서비스 사용:
> @router.post("/posts")
> def create_post(data: PostCreate, db: Session):
>     return PostService(db).create_post(data)  # 깔끔!
>
> [서비스 클래스의 역할]
> - 비즈니스 규칙 적용 (예: 게시글은 하루 10개까지만)
> - 데이터 가공 (예: 슬러그 생성, 날짜 변환)
> - 여러 모델 조합 (예: 게시글 생성 + 알림 발송)
> - 에러 처리
> ```

### 기본 서비스 클래스 (app/services/post.py)

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    """게시글 서비스"""

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db: SQLAlchemy 세션
        """
        self.db = db
```

### 라우터에서 사용

```python
from app.services.post import PostService

@router.get("/", response_model=PostListResponse)
def get_posts(db: Session = Depends(get_db)):
    post_service = PostService(db)
    posts, total = post_service.get_posts()
    return {"items": posts, "total": total}
```

---

## Create (생성)

> **초보자 안내:** Create는 **"새 데이터를 만드는 작업"**입니다.
>
> ```
> [Create 흐름]
>
> 클라이언트                    서버                      데이터베이스
>     │                          │                          │
>     │── POST /posts ──────────→│                          │
>     │   {title, content}       │                          │
>     │                          │── INSERT INTO posts... ─→│
>     │                          │                          │
>     │                          │←── 새 행 생성됨 ─────────│
>     │←─ 201 Created ───────────│                          │
>     │   {id: 1, title: ...}    │                          │
>
> [주요 단계]
> 1. 클라이언트가 데이터 전송
> 2. 입력 검증 (Pydantic)
> 3. 비즈니스 로직 처리 (Service)
> 4. 데이터베이스 저장 (Model)
> 5. 생성된 객체 반환
> ```

### 서비스 메서드

```python
def create_post(self, post_data: PostCreate, author_id: int) -> Post:
    """
    게시글 생성

    Args:
        post_data: 게시글 데이터
        author_id: 작성자 ID

    Returns:
        생성된 게시글
    """
    # 모델 인스턴스 생성
    post = Post(
        title=post_data.title,
        content=post_data.content,
        slug=generate_slug(post_data.title),
        author_id=author_id,
        category_id=post_data.category_id,
        is_published=post_data.is_published
    )

    # 세션에 추가
    self.db.add(post)

    # flush로 ID 생성 (commit 전)
    self.db.flush()

    # 슬러그에 ID 추가 (고유성 보장)
    post.slug = generate_slug(post_data.title, post.id)

    # 커밋
    self.db.commit()

    # 새로고침 (DB 값 로드)
    self.db.refresh(post)

    return post
```

### 라우터 엔드포인트

```python
@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성"
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    게시글 작성

    로그인이 필요합니다.
    """
    post_service = PostService(db)
    post = post_service.create_post(post_data, current_user.id)

    return {
        **post.__dict__,
        "author": post.author,
        "category": post.category,
        "comment_count": 0
    }
```

### 중복 검사가 필요한 경우 (사용자 생성)

```python
def create_user(self, user_data: UserCreate) -> User:
    """
    사용자 생성

    이메일과 사용자명 중복을 확인합니다.
    """
    # 이메일 중복 확인
    if self.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )

    # 사용자명 중복 확인
    if self.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다."
        )

    # 사용자 생성
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.USER
    )

    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)

    return user
```

---

## Read (조회)

> **초보자 안내:** Read는 **"데이터를 가져오는 작업"**입니다.
>
> ```
> [Read의 종류]
>
> 1. 단일 조회 (Get One)
>    GET /posts/1 → 1번 게시글 하나만
>
> 2. 목록 조회 (Get Many)
>    GET /posts → 여러 게시글 (페이지네이션)
>
> 3. 조건 조회 (Search/Filter)
>    GET /posts?category=tech → 'tech' 카테고리만
>    GET /posts?search=FastAPI → 검색어 포함된 것만
>
> [흔한 패턴]
> - 없는 데이터 요청 → 404 Not Found
> - 권한 없는 데이터 → 403 Forbidden (또는 404로 숨김)
> - 목록 조회 → 페이지네이션 필수
> ```

### 단일 항목 조회

```python
def get_post(self, post_id: int) -> Optional[Post]:
    """
    ID로 게시글 조회

    관계된 데이터(작성자, 카테고리)도 함께 로드합니다.
    """
    return self.db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.category)
    ).filter(Post.id == post_id).first()


def get_post_by_slug(self, slug: str) -> Optional[Post]:
    """슬러그로 게시글 조회"""
    return self.db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.category)
    ).filter(Post.slug == slug).first()
```

### 라우터 엔드포인트

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
        if not current_user:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        if post.author_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    post_service.increment_view_count(post_id)

    return post
```

### 목록 조회 (필터링, 검색)

```python
def get_posts(
    self,
    page: int = 1,
    size: int = 10,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    include_unpublished: bool = False
) -> Tuple[List[Post], int]:
    """
    게시글 목록 조회

    Args:
        page: 페이지 번호
        size: 페이지당 항목 수
        category_id: 카테고리 필터
        search: 검색어
        include_unpublished: 미공개 글 포함 여부

    Returns:
        (게시글 목록, 전체 개수)
    """
    query = self.db.query(Post).options(
        joinedload(Post.author),
        joinedload(Post.category)
    )

    # 공개 여부 필터
    if not include_unpublished:
        query = query.filter(Post.is_published == True)

    # 카테고리 필터
    if category_id:
        query = query.filter(Post.category_id == category_id)

    # 검색
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Post.title.ilike(search_pattern)) |
            (Post.content.ilike(search_pattern))
        )

    # 전체 개수
    total = query.count()

    # 정렬 및 페이지네이션
    posts = query.order_by(
        desc(Post.is_pinned),   # 고정글 먼저
        desc(Post.created_at)   # 최신순
    ).offset((page - 1) * size).limit(size).all()

    return posts, total
```

---

## Update (수정)

> **초보자 안내:** Update는 **"기존 데이터를 수정하는 작업"**입니다.
>
> ```
> [PUT vs PATCH]
>
> PUT (전체 교체):
>   기존 데이터 전체를 새 데이터로 교체
>   모든 필드를 보내야 함
>   PUT /posts/1 {title: "...", content: "...", category: "...", ...}
>
> PATCH (부분 수정):
>   변경하고 싶은 필드만 보냄
>   나머지는 그대로 유지
>   PATCH /posts/1 {title: "새 제목"}  ← 제목만 수정
>
> [이 프로젝트에서는]
> - PUT을 사용하지만 PATCH처럼 동작
> - 보내지 않은 필드(None)는 수정하지 않음
>
> [권한 확인 중요!]
> - 본인 게시글만 수정 가능
> - 관리자는 모든 게시글 수정 가능
> ```

### 서비스 메서드

```python
def update_post(
    self,
    post_id: int,
    post_data: PostUpdate,
    user: User
) -> Post:
    """
    게시글 수정

    Args:
        post_id: 게시글 ID
        post_data: 수정할 데이터
        user: 요청한 사용자

    Returns:
        수정된 게시글

    Raises:
        HTTPException: 권한이 없거나 게시글이 없는 경우
    """
    post = self.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 권한 확인 (작성자 또는 관리자)
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수정 권한이 없습니다."
        )

    # 필드 업데이트 (None이 아닌 값만)
    if post_data.title is not None:
        post.title = post_data.title
        post.slug = generate_slug(post_data.title, post.id)

    if post_data.content is not None:
        post.content = post_data.content

    if post_data.category_id is not None:
        post.category_id = post_data.category_id

    if post_data.is_published is not None:
        post.is_published = post_data.is_published

    if post_data.is_pinned is not None:
        post.is_pinned = post_data.is_pinned

    # 커밋
    self.db.commit()
    self.db.refresh(post)

    return post
```

### 부분 업데이트 (PATCH) 스키마

```python
class PostUpdate(BaseModel):
    """
    게시글 수정 스키마

    모든 필드가 선택적입니다.
    """
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_pinned: Optional[bool] = None
```

### 라우터 엔드포인트

```python
@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """게시글 수정"""
    post_service = PostService(db)
    post = post_service.update_post(post_id, post_data, current_user)

    return {
        **post.__dict__,
        "author": post.author,
        "category": post.category,
        "comment_count": post_service.get_comment_count(post_id)
    }
```

---

## Delete (삭제)

> **초보자 안내:** Delete는 **"데이터를 제거하는 작업"**입니다.
>
> ```
> [하드 삭제 vs 소프트 삭제]
>
> 하드 삭제 (Hard Delete):
>   DELETE FROM posts WHERE id = 1
>   → 데이터가 완전히 사라짐
>   → 복구 불가능
>   → 관련 데이터도 함께 삭제 (cascade)
>
> 소프트 삭제 (Soft Delete):
>   UPDATE posts SET is_deleted = true WHERE id = 1
>   → 데이터는 남아있음
>   → 복구 가능
>   → 조회 시 is_deleted = false 조건 필요
>
> [언제 무엇을 쓸까?]
> 하드 삭제: 임시 데이터, 개인정보 삭제 요청
> 소프트 삭제: 실수 복구 필요, 삭제 이력 보관 필요
>
> [HTTP 응답]
> DELETE /posts/1 → 204 No Content (본문 없음)
> ```

### 하드 삭제

```python
def delete_post(self, post_id: int, user: User) -> bool:
    """
    게시글 삭제

    관련 댓글도 함께 삭제됩니다 (cascade).
    """
    post = self.get_post(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    # 권한 확인
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다."
        )

    self.db.delete(post)
    self.db.commit()

    return True
```

### 소프트 삭제 (권장)

```python
def delete_comment(self, comment_id: int, user: User) -> bool:
    """
    댓글 소프트 삭제

    실제로 삭제하지 않고 is_active를 False로 설정합니다.
    """
    comment = self.db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )

    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다."
        )

    # 소프트 삭제
    comment.is_active = False
    comment.content = "삭제된 댓글입니다."

    self.db.commit()

    return True
```

### 라우터 엔드포인트

```python
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """게시글 삭제"""
    post_service = PostService(db)
    post_service.delete_post(post_id, current_user)
    # 204 No Content - 본문 없이 반환
```

---

## 페이지네이션

> **초보자 안내:** 페이지네이션은 **"데이터를 나눠서 가져오는 방식"**입니다.
>
> ```
> [왜 페이지네이션이 필요한가요?]
>
> 게시글이 10,000개라면?
> ❌ 한 번에 다 가져오기 → 서버 과부하, 느린 응답
> ✅ 10개씩 나눠서 가져오기 → 빠른 응답, 효율적
>
> [오프셋 기반 vs 커서 기반]
>
> 오프셋 기반 (전통적):
>   GET /posts?page=2&size=10
>   → OFFSET 10 LIMIT 10 (11번째부터 10개)
>   ✅ 구현 쉬움, "3페이지로 이동" 가능
>   ❌ 대용량에서 느림 (OFFSET이 클수록)
>
> 커서 기반 (현대적):
>   GET /posts?cursor=100&size=10
>   → WHERE id < 100 LIMIT 10
>   ✅ 대용량에서도 빠름
>   ❌ "3페이지로 이동" 불가, 무한스크롤에 적합
>
> [응답 형식]
> {
>   "items": [...],      // 실제 데이터
>   "total": 150,        // 전체 개수
>   "page": 2,           // 현재 페이지
>   "size": 10,          // 페이지당 개수
>   "pages": 15          // 전체 페이지 수
> }
> ```

### 응답 스키마

```python
from typing import List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PostListResponse(BaseModel):
    """페이지네이션된 게시글 목록"""
    items: List[PostResponse] = Field(..., description="게시글 목록")
    total: int = Field(..., description="전체 게시글 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지당 항목 수")
    pages: int = Field(..., description="전체 페이지 수")
```

### 라우터에서 구현

```python
from math import ceil

@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=50, description="페이지당 항목 수"),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """게시글 목록 조회 (페이지네이션)"""
    post_service = PostService(db)

    include_unpublished = current_user and current_user.is_admin

    posts, total = post_service.get_posts(
        page=page,
        size=size,
        category_id=category_id,
        search=search,
        include_unpublished=include_unpublished
    )

    # 댓글 수 추가
    items = []
    for post in posts:
        items.append({
            **post.__dict__,
            "author": post.author,
            "category": post.category,
            "comment_count": post_service.get_comment_count(post.id)
        })

    return PostListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 0
    )
```

### 커서 기반 페이지네이션 (대용량)

```python
def get_posts_cursor(
    self,
    cursor: Optional[int] = None,
    size: int = 10
) -> Tuple[List[Post], Optional[int]]:
    """
    커서 기반 페이지네이션

    대용량 데이터에서 더 효율적입니다.

    Args:
        cursor: 마지막으로 본 게시글 ID
        size: 가져올 항목 수

    Returns:
        (게시글 목록, 다음 커서)
    """
    query = self.db.query(Post).filter(Post.is_published == True)

    if cursor:
        query = query.filter(Post.id < cursor)

    posts = query.order_by(desc(Post.id)).limit(size + 1).all()

    # 다음 페이지 존재 여부 확인
    has_next = len(posts) > size
    if has_next:
        posts = posts[:size]
        next_cursor = posts[-1].id
    else:
        next_cursor = None

    return posts, next_cursor
```

---

## 실수하기 쉬운 부분

> **초보자 안내:** CRUD 구현 시 흔히 발생하는 실수들입니다.

### 1. commit 없이 데이터 저장 기대

```python
# ❌ 잘못된 코드 - 데이터가 저장되지 않음!
def create_post(self, data: PostCreate) -> Post:
    post = Post(title=data.title, content=data.content)
    self.db.add(post)
    # commit 없음!
    return post

# ✅ 올바른 코드
def create_post(self, data: PostCreate) -> Post:
    post = Post(title=data.title, content=data.content)
    self.db.add(post)
    self.db.commit()       # 반드시 commit!
    self.db.refresh(post)  # DB에서 다시 로드 (id 등 자동 생성된 값 반영)
    return post
```

### 2. 권한 확인 누락

```python
# ❌ 잘못된 코드 - 아무나 수정 가능!
def update_post(self, post_id: int, data: PostUpdate) -> Post:
    post = self.get_post(post_id)
    post.title = data.title
    self.db.commit()
    return post

# ✅ 올바른 코드 - 권한 확인
def update_post(self, post_id: int, data: PostUpdate, user: User) -> Post:
    post = self.get_post(post_id)

    # 작성자 또는 관리자만 수정 가능
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    post.title = data.title
    self.db.commit()
    return post
```

### 3. N+1 쿼리 문제

```python
# ❌ 잘못된 코드 - 게시글 10개면 쿼리 11번 실행!
def get_posts(self):
    posts = self.db.query(Post).limit(10).all()
    for post in posts:
        print(post.author.username)  # 각 게시글마다 author 조회 쿼리 실행
    return posts

# ✅ 올바른 코드 - joinedload로 한 번에 로드
from sqlalchemy.orm import joinedload

def get_posts(self):
    posts = self.db.query(Post).options(
        joinedload(Post.author)  # author를 미리 로드
    ).limit(10).all()
    for post in posts:
        print(post.author.username)  # 추가 쿼리 없음!
    return posts
```

### 4. 존재하지 않는 데이터 처리 누락

```python
# ❌ 잘못된 코드 - None 체크 안 함
@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    return post  # post가 None이면 null 반환 (또는 에러)

# ✅ 올바른 코드
@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post
```

### 5. 하드코딩된 페이지 크기

```python
# ❌ 잘못된 코드 - 페이지 크기 고정
def get_posts(self, page: int):
    return self.db.query(Post).offset((page-1) * 10).limit(10).all()

# ✅ 올바른 코드 - 유연한 페이지 크기 (제한 포함)
def get_posts(self, page: int = 1, size: int = 10):
    size = min(size, 100)  # 최대 100개로 제한 (악의적 요청 방지)
    return self.db.query(Post).offset((page-1) * size).limit(size).all()
```

---

## 요약

| 작업 | HTTP 메서드 | 주요 포인트 |
|------|-------------|------------|
| Create | POST | `add()` → `commit()` → `refresh()` |
| Read | GET | `joinedload`로 N+1 방지, 404 처리 |
| Update | PUT/PATCH | 권한 확인, None 필드는 건너뛰기 |
| Delete | DELETE | 하드/소프트 선택, cascade 고려 |
| 페이지네이션 | GET (쿼리) | 오프셋 또는 커서 기반 선택 |

---

## 다음 단계

CRUD 패턴을 이해했다면:

- **[테스트](06_testing.md)**: CRUD 작업을 테스트하는 방법 배우기

> **팁:** 테스트를 작성하면 CRUD 로직이 올바르게 작동하는지 확인할 수 있습니다.

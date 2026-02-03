# 데이터베이스

이 문서에서는 FastAPI에서 SQLAlchemy를 사용한 데이터베이스 작업을 설명합니다.

> **이 문서를 읽기 전에**: [FastAPI 기본 문법](01_fastapi_basics.md)과 [라우팅](02_routing.md)을 먼저 읽으면 이해가 쉽습니다.

## 데이터베이스란?

> **초보자 안내:** 데이터베이스(DB)는 **데이터를 체계적으로 저장하고 관리하는 곳**입니다.
>
> 엑셀 스프레드시트를 생각해 보세요:
> ```
> [users 테이블 = 엑셀 시트]
>
> id | email              | username | password_hash | created_at
> ---+--------------------+----------+---------------+------------
>  1 | alice@example.com  | alice    | abc123...     | 2024-01-01
>  2 | bob@example.com    | bob      | def456...     | 2024-01-02
>  3 | carol@example.com  | carol    | ghi789...     | 2024-01-03
>
> - 테이블 = 엑셀 시트 (users, posts, comments...)
> - 행(Row) = 데이터 한 개 (1번 사용자, 2번 사용자...)
> - 열(Column) = 데이터 속성 (email, username...)
> ```
>
> **왜 엑셀 대신 데이터베이스를 사용하나요?**
>
> | 기능 | 엑셀 | 데이터베이스 |
> |------|------|-------------|
> | 동시 접속 | 한 명만 | 수천 명 동시 가능 |
> | 데이터 양 | 수만 행 한계 | 수억 행 가능 |
> | 검색 속도 | 느림 | 빠름 (인덱스) |
> | 데이터 무결성 | 보장 안 됨 | 제약조건으로 보장 |

## 목차

1. [SQLAlchemy 소개](#sqlalchemy-소개)
2. [SQLAlchemy 설정](#sqlalchemy-설정)
3. [모델 정의](#모델-정의)
4. [관계 설정](#관계-설정)
5. [CRUD 작업](#crud-작업)
6. [쿼리 작성](#쿼리-작성)
7. [마이그레이션](#마이그레이션)

---

## SQLAlchemy 소개

### SQLAlchemy란?

> **초보자 안내:** SQLAlchemy는 **Python 코드로 데이터베이스를 다루게 해주는 도구**입니다.
>
> 보통 데이터베이스는 SQL이라는 언어로 다룹니다:
> ```sql
> -- SQL: 데이터베이스 전용 언어
> SELECT * FROM users WHERE email = 'alice@example.com';
> INSERT INTO users (email, username) VALUES ('bob@example.com', 'bob');
> ```
>
> SQLAlchemy를 사용하면 Python으로 같은 작업을 할 수 있습니다:
> ```python
> # Python (SQLAlchemy ORM)
> user = db.query(User).filter(User.email == 'alice@example.com').first()
> new_user = User(email='bob@example.com', username='bob')
> db.add(new_user)
> ```
>
> **장점:**
> - SQL을 몰라도 데이터베이스 사용 가능
> - Python 문법 그대로 사용
> - 타입 힌트와 자동완성 지원
> - 다양한 DB(PostgreSQL, MySQL, SQLite) 지원

### ORM이란?

> **초보자 안내:** ORM(Object-Relational Mapping)은 **데이터베이스 테이블을 Python 클래스로 표현**하는 방식입니다.
>
> ```
> [데이터베이스 테이블]              [Python 클래스]
>
> users 테이블                  →   class User:
> ┌────┬─────────────┐              id: int
> │ id │ email       │              email: str
> ├────┼─────────────┤              username: str
> │  1 │ alice@...   │
> │  2 │ bob@...     │
> └────┴─────────────┘
>
> 테이블의 각 행 = User 객체 하나
> ```
>
> 비유: 번역기
> - SQL을 모르는 Python 개발자
> - Python 코드를 쓰면 SQLAlchemy가 SQL로 번역해서 DB에 전달
> - DB 결과를 다시 Python 객체로 번역해서 반환

---

## SQLAlchemy 설정

### 기본 설정 (app/database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 데이터베이스 URL 생성
def get_engine():
    """DB 타입에 따라 엔진 생성"""
    database_url = settings.database_url

    if settings.db_type == "sqlite":
        # SQLite 특수 설정
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL, MySQL
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # 연결 유효성 검사
            pool_size=10,        # 커넥션 풀 크기
            max_overflow=20,     # 최대 추가 연결
            echo=settings.debug  # SQL 로깅
        )

    return engine

# 엔진 생성
engine = get_engine()

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 모델 기본 클래스
Base = declarative_base()
```

> **코드 해석:**
>
> | 코드 | 하는 일 | 비유 |
> |------|---------|------|
> | `create_engine()` | DB 연결 설정 생성 | 전화선 설치 |
> | `SessionLocal` | DB 대화 창구 공장 | 상담 창구 매뉴얼 |
> | `Base` | 모든 모델의 부모 클래스 | 모델 틀 |
>
> **커넥션 풀이란?**
> ```
> [커넥션 풀 = 수영장 레인]
>
> DB 연결을 미리 10개 만들어 두고 (pool_size=10)
> 요청이 오면 빈 연결을 빌려줌
> 요청이 끝나면 연결을 반납 (닫지 않고 재사용)
>
> ┌─────────────────────────────────┐
> │        커넥션 풀 (10개)          │
> │  [연결1] [연결2] [연결3] ... [연결10]  │
> └─────────────────────────────────┘
>        ↑       ↑       ↑
>      요청1   요청2   요청3
>
> 매번 새 연결을 만드는 것보다 훨씬 빠름!
> ```

### 세션 의존성

```python
from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 제공

    FastAPI의 Depends()와 함께 사용합니다.
    요청마다 새 세션을 생성하고 자동으로 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

> **초보자 안내:** `get_db()`의 동작 순서:
>
> ```
> 1. API 요청 들어옴
> 2. db = SessionLocal() → 새 세션 생성
> 3. yield db → 세션을 API 함수에 전달
> 4. API 함수 실행 (DB 작업)
> 5. finally: db.close() → 세션 자동 종료
> ```
>
> `yield`와 `finally` 덕분에 DB 연결이 항상 정리됩니다!

### 사용 예시

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

> **초보자 안내:** `db: Session = Depends(get_db)`의 의미:
>
> "이 함수를 실행하기 전에 `get_db()`를 먼저 실행해서 `db`를 준비해줘"
>
> 덕분에 매번 DB 연결 코드를 쓸 필요가 없습니다!

---

## 모델 정의

### 모델이란?

> **초보자 안내:** 모델은 **데이터베이스 테이블을 Python 클래스로 표현한 것**입니다.
>
> ```python
> # 이 Python 클래스가...
> class User(Base):
>     __tablename__ = "users"
>     id = Column(Integer, primary_key=True)
>     email = Column(String(255))
>     username = Column(String(50))
> ```
>
> ```
> # ...이 데이터베이스 테이블이 됩니다
> CREATE TABLE users (
>     id INTEGER PRIMARY KEY,
>     email VARCHAR(255),
>     username VARCHAR(50)
> );
> ```

### 기본 모델 (app/models/user.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """사용자 역할 열거형"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class User(Base):
    """사용자 모델"""

    # 테이블 이름
    __tablename__ = "users"

    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # 열거형 컬럼
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False
    )

    # 불리언 컬럼
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 관계 정의
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

    @property
    def is_admin(self) -> bool:
        """관리자 여부"""
        return self.role == UserRole.ADMIN
```

> **코드 해석:**
>
> | 코드 | 의미 |
> |------|------|
> | `__tablename__ = "users"` | DB에서 테이블 이름은 "users" |
> | `primary_key=True` | 이 컬럼이 기본 키 (유일한 식별자) |
> | `unique=True` | 중복 값 불가 (같은 이메일 두 번 등록 불가) |
> | `index=True` | 검색 속도 향상을 위한 인덱스 생성 |
> | `nullable=False` | NULL 불가 (필수 입력) |
> | `default=UserRole.USER` | 기본값 설정 |
> | `onupdate=datetime.utcnow` | 수정할 때마다 자동으로 현재 시간 기록 |

### 컬럼 타입 정리

| SQLAlchemy 타입 | Python 타입 | SQL 타입 | 설명 |
|----------------|-------------|----------|------|
| `Integer` | `int` | INTEGER | 정수 |
| `String(n)` | `str` | VARCHAR(n) | 길이 제한 문자열 |
| `Text` | `str` | TEXT | 긴 문자열 |
| `Float` | `float` | FLOAT | 소수점 숫자 |
| `Boolean` | `bool` | BOOLEAN | 참/거짓 |
| `DateTime` | `datetime` | TIMESTAMP | 날짜+시간 |
| `Date` | `date` | DATE | 날짜만 |
| `JSON` | `dict` | JSON | JSON 데이터 |

### 컬럼 옵션 정리

```python
Column(
    String(255),
    primary_key=True,     # 기본 키 (테이블당 1개)
    unique=True,          # 중복 불가
    index=True,           # 검색 빠르게 (인덱스)
    nullable=False,       # NULL 불가 (필수)
    default="value",      # Python 기본값
    server_default="now()",  # DB 레벨 기본값
    onupdate=datetime.utcnow  # 수정 시 자동 갱신
)
```

> **초보자 안내:** 인덱스(index)란?
>
> ```
> [인덱스 없이 검색]
> "alice@example.com을 찾아라"
> → 처음부터 끝까지 1,000,000개 데이터를 하나씩 확인 (느림)
>
> [인덱스 있으면]
> "alice@example.com을 찾아라"
> → 인덱스(목차)에서 바로 위치 확인 → 바로 찾음 (빠름)
>
> 책의 목차처럼, 자주 검색하는 컬럼에는 인덱스를 걸어두세요!
> ```

---

## 관계 설정

### 관계란?

> **초보자 안내:** 관계(Relationship)는 **테이블 간의 연결**입니다.
>
> ```
> [현실 세계의 관계]
>
> 사용자 ──┬── 게시글1
>         ├── 게시글2
>         └── 게시글3
>
> "한 명의 사용자가 여러 개의 게시글을 작성할 수 있다"
> ```
>
> 이것을 데이터베이스로 표현하면:
> ```
> users 테이블              posts 테이블
> ┌────┬─────────┐         ┌────┬───────────┬───────────┐
> │ id │ name    │         │ id │ title     │ author_id │
> ├────┼─────────┤         ├────┼───────────┼───────────┤
> │  1 │ alice   │    ←────│  1 │ 첫 글     │     1     │
> │  2 │ bob     │    ←────│  2 │ 두번째 글 │     1     │
> └────┴─────────┘         │  3 │ bob의 글  │     2     │
>                          └────┴───────────┴───────────┘
>                                              ↑
>                               이 컬럼이 users.id를 참조 (외래 키)
> ```

### 일대다 관계 (1:N)

가장 흔한 관계입니다. 예: 한 명의 사용자가 여러 게시글을 작성

```python
# User 모델 (1쪽)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # ...

    # 관계 정의: "이 사용자의 게시글들"
    posts = relationship(
        "Post",                    # 연결할 모델
        back_populates="author",   # Post 모델의 author 속성과 연결
        cascade="all, delete-orphan"  # 사용자 삭제 시 게시글도 삭제
    )


# Post 모델 (N쪽)
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)

    # 외래 키: "이 게시글의 작성자 ID"
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 관계 정의: "이 게시글의 작성자"
    author = relationship("User", back_populates="posts")
```

> **코드 사용 예시:**
>
> ```python
> # 사용자의 모든 게시글 가져오기
> user = db.query(User).first()
> user.posts  # [Post1, Post2, Post3, ...]
>
> # 게시글의 작성자 가져오기
> post = db.query(Post).first()
> post.author  # User 객체
> post.author.username  # "alice"
> ```

### 다대다 관계 (N:N)

예: 게시글과 태그 (한 게시글에 여러 태그, 한 태그가 여러 게시글에)

```python
# 연결 테이블 (중간 테이블)
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)

    # 다대다 관계
    tags = relationship(
        "Tag",
        secondary=post_tags,  # 연결 테이블 지정
        back_populates="posts"
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    posts = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags"
    )
```

> **초보자 안내:** 다대다 관계는 **연결 테이블**이 필요합니다:
>
> ```
> posts        post_tags (연결 테이블)     tags
> ┌────┐      ┌─────────┬────────┐      ┌────┬─────────┐
> │ id │      │ post_id │ tag_id │      │ id │ name    │
> ├────┤      ├─────────┼────────┤      ├────┼─────────┤
> │  1 │──────│    1    │   1    │──────│  1 │ python  │
> │    │──────│    1    │   2    │──────│  2 │ fastapi │
> │  2 │──────│    2    │   1    │      │  3 │ web     │
> └────┘      └─────────┴────────┘      └────┴─────────┘
>
> 게시글 1 → 태그: python, fastapi
> 게시글 2 → 태그: python
> ```

### 자기 참조 관계 (app/models/post.py)

예: 댓글과 대댓글

```python
class Comment(Base):
    """댓글 모델 (대댓글 지원)"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)

    # 게시글 관계
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    post = relationship("Post", back_populates="comments")

    # 작성자 관계
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="comments")

    # 자기 참조 (대댓글)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    parent = relationship(
        "Comment",
        remote_side=[id],  # 자기 참조임을 명시
        backref="replies"
    )
```

> **초보자 안내:** 자기 참조는 **같은 테이블 내에서 관계**를 만드는 것입니다:
>
> ```
> comments 테이블
> ┌────┬─────────────┬───────────┐
> │ id │ content     │ parent_id │
> ├────┼─────────────┼───────────┤
> │  1 │ "첫 댓글"    │   NULL    │  ← 원댓글
> │  2 │ "대댓글1"    │     1     │  ← 1번의 대댓글
> │  3 │ "대댓글2"    │     1     │  ← 1번의 대댓글
> │  4 │ "대대댓글"   │     2     │  ← 2번의 대댓글
> └────┴─────────────┴───────────┘
> ```

---

## CRUD 작업

### CRUD란?

> **초보자 안내:** CRUD는 데이터베이스의 **4가지 기본 작업**입니다:
>
> | 작업 | 의미 | SQL | Python (SQLAlchemy) |
> |------|------|-----|---------------------|
> | **C**reate | 생성 | INSERT | `db.add(obj)` |
> | **R**ead | 조회 | SELECT | `db.query().all()` |
> | **U**pdate | 수정 | UPDATE | `obj.field = value` |
> | **D**elete | 삭제 | DELETE | `db.delete(obj)` |

### Create (생성)

```python
def create_user(db: Session, user_data: UserCreate) -> User:
    """사용자 생성"""
    # 1. 객체 생성
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password)
    )

    # 2. 세션에 추가 (아직 DB에 저장 안 됨)
    db.add(user)

    # 3. DB에 저장 (커밋)
    db.commit()

    # 4. DB에서 다시 로드 (자동 생성된 ID 등 갱신)
    db.refresh(user)

    return user
```

> **초보자 안내:** 저장 과정:
>
> ```
> db.add(user)    →  "이 데이터 저장할 거야" (예약)
> db.commit()     →  "진짜 저장해!" (실제 저장)
> db.refresh(user) → "저장된 최신 데이터로 갱신해줘" (ID 등 가져옴)
> ```
>
> 왜 `commit()` 전까지 저장이 안 될까요?
> - 여러 작업을 묶어서 처리 가능 (트랜잭션)
> - 중간에 오류나면 전체 취소 가능 (롤백)

### Read (조회)

```python
def get_user(db: Session, user_id: int) -> Optional[User]:
    """ID로 사용자 조회"""
    return db.query(User).filter(User.id == user_id).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """사용자 목록 조회"""
    return db.query(User).offset(skip).limit(limit).all()
```

> **코드 해석:**
>
> | 메서드 | 의미 |
> |--------|------|
> | `db.query(User)` | User 테이블에서 조회 시작 |
> | `.filter(User.id == 1)` | id가 1인 것만 |
> | `.first()` | 첫 번째 결과 (없으면 None) |
> | `.all()` | 모든 결과 (리스트) |
> | `.offset(10)` | 10개 건너뛰고 |
> | `.limit(5)` | 5개만 |

### Update (수정)

```python
def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
) -> Optional[User]:
    """사용자 정보 수정"""
    # 1. 기존 데이터 조회
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    # 2. 제공된 필드만 업데이트
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    # 3. 저장
    db.commit()
    db.refresh(user)

    return user
```

> **초보자 안내:** `exclude_unset=True`의 의미:
>
> ```python
> # user_data = {"username": "new_name"}  (email은 안 보냄)
>
> user_data.model_dump(exclude_unset=True)
> # → {"username": "new_name"}  (보낸 것만)
>
> user_data.model_dump(exclude_unset=False)
> # → {"username": "new_name", "email": None, ...}  (안 보낸 것은 None)
> ```
>
> `exclude_unset=True`를 써야 **보낸 필드만** 수정됩니다!

### Delete (삭제)

```python
def delete_user(db: Session, user_id: int) -> bool:
    """사용자 삭제"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    db.delete(user)
    db.commit()

    return True
```

### 프로젝트 예시 (app/services/post.py)

```python
class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, post_data: PostCreate, author_id: int) -> Post:
        """게시글 생성"""
        post = Post(
            title=post_data.title,
            content=post_data.content,
            slug=generate_slug(post_data.title),
            author_id=author_id,
            category_id=post_data.category_id,
            is_published=post_data.is_published
        )

        self.db.add(post)
        self.db.flush()  # ID 생성을 위해 flush (커밋은 아직)

        # 슬러그에 ID 추가
        post.slug = generate_slug(post_data.title, post.id)

        self.db.commit()
        self.db.refresh(post)

        return post
```

> **초보자 안내:** `flush()` vs `commit()`:
>
> | 메서드 | 하는 일 | 취소 가능? |
> |--------|---------|-----------|
> | `flush()` | DB에 보내기만 함 (ID 생성됨) | 가능 (rollback) |
> | `commit()` | 실제 저장 확정 | 불가능 |
>
> `flush()`는 ID가 필요하지만 아직 저장 확정하고 싶지 않을 때 사용합니다.

---

## 쿼리 작성

### 기본 쿼리

```python
# 전체 조회
users = db.query(User).all()

# 첫 번째 결과
user = db.query(User).first()

# 특정 ID
user = db.query(User).get(1)  # 또는
user = db.query(User).filter(User.id == 1).first()
```

### 필터링

```python
# 단일 조건
users = db.query(User).filter(User.is_active == True).all()

# 여러 조건 (AND)
users = db.query(User).filter(
    User.is_active == True,
    User.role == UserRole.ADMIN
).all()

# OR 조건
from sqlalchemy import or_

users = db.query(User).filter(
    or_(
        User.email == email,
        User.username == username
    )
).first()

# LIKE 검색 (부분 일치)
posts = db.query(Post).filter(
    Post.title.ilike(f"%{search}%")  # 대소문자 무시
).all()

# IN 조건
users = db.query(User).filter(
    User.id.in_([1, 2, 3])
).all()

# NULL 체크
users = db.query(User).filter(
    User.last_login.is_(None)
).all()
```

> **초보자 안내:** 필터 조건 정리:
>
> | 조건 | SQLAlchemy | SQL |
> |------|-----------|-----|
> | 같음 | `User.id == 1` | `id = 1` |
> | 다름 | `User.id != 1` | `id != 1` |
> | 크다 | `User.age > 20` | `age > 20` |
> | 포함 | `Post.title.ilike("%검색어%")` | `title LIKE '%검색어%'` |
> | 목록 | `User.id.in_([1,2,3])` | `id IN (1,2,3)` |
> | NULL | `User.field.is_(None)` | `field IS NULL` |

### 정렬

```python
from sqlalchemy import desc, asc

# 내림차순 (최신순)
posts = db.query(Post).order_by(desc(Post.created_at)).all()

# 오름차순 (오래된순)
posts = db.query(Post).order_by(asc(Post.title)).all()

# 여러 컬럼
posts = db.query(Post).order_by(
    desc(Post.is_pinned),   # 고정글 먼저
    desc(Post.created_at)   # 그 다음 최신순
).all()
```

### 페이지네이션

```python
def get_posts(
    db: Session,
    page: int = 1,
    size: int = 10
) -> tuple[list[Post], int]:
    """페이지네이션된 게시글 조회"""

    query = db.query(Post).filter(Post.is_published == True)

    # 전체 개수
    total = query.count()

    # 페이지네이션
    posts = query.order_by(
        desc(Post.created_at)
    ).offset((page - 1) * size).limit(size).all()

    return posts, total
```

> **초보자 안내:** 페이지네이션 계산:
>
> ```
> 총 데이터: 100개, 페이지당 10개
>
> 1페이지: offset(0), limit(10)  → 1~10번
> 2페이지: offset(10), limit(10) → 11~20번
> 3페이지: offset(20), limit(10) → 21~30번
>
> offset = (page - 1) * size
> ```

### 조인과 관계 로딩

```python
from sqlalchemy.orm import joinedload

# Eager loading (N+1 문제 해결)
posts = db.query(Post).options(
    joinedload(Post.author),
    joinedload(Post.category)
).all()

# 명시적 조인
posts = db.query(Post).join(User).filter(
    User.is_active == True
).all()
```

> **초보자 안내:** N+1 문제란?
>
> ```
> # ❌ 문제 상황 (joinedload 없이)
> posts = db.query(Post).all()    # 쿼리 1번
> for post in posts:
>     print(post.author.name)     # 각 게시글마다 쿼리 1번씩!
>
> # 게시글 100개면 → 쿼리 101번 (1 + 100)
> ```
>
> ```
> # ✅ 해결 (joinedload 사용)
> posts = db.query(Post).options(joinedload(Post.author)).all()
>
> # 쿼리 1번에 author 정보도 함께 가져옴!
> ```

### 집계 함수

```python
from sqlalchemy import func

# COUNT
total = db.query(func.count(Post.id)).scalar()

# 조건부 COUNT
active_users = db.query(func.count(User.id)).filter(
    User.is_active == True
).scalar()

# GROUP BY
category_counts = db.query(
    Post.category_id,
    func.count(Post.id).label("count")
).group_by(Post.category_id).all()
```

### 프로젝트 예시 (app/services/post.py)

```python
def get_posts(
    self,
    page: int = 1,
    size: int = 10,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    include_unpublished: bool = False
) -> Tuple[List[Post], int]:
    """게시글 목록 조회 (필터링, 페이지네이션)"""

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
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern)
            )
        )

    # 전체 개수
    total = query.count()

    # 정렬 및 페이지네이션
    posts = query.order_by(
        desc(Post.is_pinned),
        desc(Post.created_at)
    ).offset((page - 1) * size).limit(size).all()

    return posts, total
```

---

## 마이그레이션

### 마이그레이션이란?

> **초보자 안내:** 마이그레이션은 **데이터베이스 구조를 버전 관리**하는 것입니다.
>
> ```
> [마이그레이션 = 데이터베이스의 Git]
>
> 코드 변경 이력처럼, DB 구조 변경도 기록합니다:
>
> 버전 1: users 테이블 생성
> 버전 2: users에 phone 컬럼 추가
> 버전 3: posts 테이블 생성
> 버전 4: posts에 is_pinned 컬럼 추가
>
> 언제든 특정 버전으로 돌아갈 수 있습니다!
> ```
>
> **왜 필요한가요?**
> - 팀원들과 DB 구조 동기화
> - 운영 서버에 안전하게 변경 적용
> - 문제 발생 시 롤백 가능

### Alembic 설정

```bash
# 초기화 (이미 완료됨)
alembic init alembic
```

### 마이그레이션 생성

```bash
# 자동 생성 (모델 변경 감지)
alembic revision --autogenerate -m "Add users table"

# 수동 생성 (직접 작성)
alembic revision -m "Add custom migration"
```

> **초보자 안내:** `--autogenerate`를 쓰면 SQLAlchemy 모델과 실제 DB를 비교해서 자동으로 마이그레이션 파일을 만들어 줍니다.

### 마이그레이션 적용

```bash
# 최신으로 업그레이드
alembic upgrade head

# 특정 버전으로
alembic upgrade <revision_id>

# 한 단계 다운그레이드 (롤백)
alembic downgrade -1

# 특정 버전으로 다운그레이드
alembic downgrade <revision_id>
```

### 마이그레이션 상태 확인

```bash
# 현재 버전
alembic current

# 히스토리
alembic history

# 적용 안 된 마이그레이션
alembic heads
```

### 마이그레이션 파일 예시

```python
# alembic/versions/xxx_add_users_table.py

def upgrade() -> None:
    """테이블 생성 (버전 올릴 때)"""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


def downgrade() -> None:
    """테이블 삭제 (버전 내릴 때)"""
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
```

> **초보자 안내:** 마이그레이션 파일에는 두 함수가 있습니다:
> - `upgrade()`: 버전 올릴 때 실행 (테이블 생성, 컬럼 추가 등)
> - `downgrade()`: 버전 내릴 때 실행 (upgrade의 반대 작업)

---

## 실수하기 쉬운 부분

### 1. 세션 닫지 않기

```python
# ❌ 잘못된 예
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    return user  # db.close() 안 함! → 연결 누수

# ✅ 올바른 예: Depends(get_db) 사용
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

### 2. commit 없이 변경

```python
# ❌ 잘못된 예
user.username = "new_name"
# commit() 안 함! → 변경이 저장되지 않음

# ✅ 올바른 예
user.username = "new_name"
db.commit()
```

### 3. N+1 문제

```python
# ❌ 잘못된 예 (쿼리 101번)
posts = db.query(Post).all()
for post in posts:
    print(post.author.username)

# ✅ 올바른 예 (쿼리 1번)
posts = db.query(Post).options(joinedload(Post.author)).all()
for post in posts:
    print(post.author.username)
```

---

## 다음 단계

- [인증](04_authentication.md) - JWT 인증 구현하기
- [CRUD 작업](05_crud.md) - 서비스 레이어 패턴
- [라우팅](02_routing.md) - API 엔드포인트 복습

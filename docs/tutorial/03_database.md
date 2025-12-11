# 데이터베이스

이 문서에서는 FastAPI에서 SQLAlchemy를 사용한 데이터베이스 작업을 설명합니다.

## 목차

1. [SQLAlchemy 설정](#sqlalchemy-설정)
2. [모델 정의](#모델-정의)
3. [관계 설정](#관계-설정)
4. [CRUD 작업](#crud-작업)
5. [쿼리 작성](#쿼리-작성)
6. [마이그레이션](#마이그레이션)

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

### 사용 예시

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

---

## 모델 정의

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

### 컬럼 타입

| SQLAlchemy 타입 | Python 타입 | SQL 타입 |
|----------------|-------------|----------|
| `Integer` | `int` | INTEGER |
| `String(n)` | `str` | VARCHAR(n) |
| `Text` | `str` | TEXT |
| `Float` | `float` | FLOAT |
| `Boolean` | `bool` | BOOLEAN |
| `DateTime` | `datetime` | TIMESTAMP |
| `Date` | `date` | DATE |
| `JSON` | `dict` | JSON |

### 컬럼 옵션

```python
Column(
    String(255),
    primary_key=True,     # 기본 키
    unique=True,          # 유니크 제약
    index=True,           # 인덱스 생성
    nullable=False,       # NOT NULL
    default="value",      # 기본값
    server_default="now()",  # DB 레벨 기본값
    onupdate=datetime.utcnow  # 업데이트 시 자동 갱신
)
```

---

## 관계 설정

### 일대다 관계

```python
# 사용자 (1) - 게시글 (N)

# User 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # ...

    # 관계 정의 (일)
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan"  # 사용자 삭제 시 게시글도 삭제
    )


# Post 모델
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)

    # 외래 키 (다)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 관계 정의 (다)
    author = relationship("User", back_populates="posts")
```

### 다대다 관계

```python
# 연결 테이블
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
        secondary=post_tags,
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

### 자기 참조 관계 (app/models/post.py)

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

---

## CRUD 작업

### Create (생성)

```python
def create_user(db: Session, user_data: UserCreate) -> User:
    """사용자 생성"""
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password)
    )

    db.add(user)           # 세션에 추가
    db.commit()            # 커밋
    db.refresh(user)       # DB에서 다시 로드 (ID 등 갱신)

    return user
```

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

### Update (수정)

```python
def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
) -> Optional[User]:
    """사용자 정보 수정"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    # 제공된 필드만 업데이트
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user
```

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
        self.db.flush()  # ID 생성을 위해 flush

        # 슬러그에 ID 추가
        post.slug = generate_slug(post_data.title, post.id)

        self.db.commit()
        self.db.refresh(post)

        return post
```

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

# LIKE 검색
posts = db.query(Post).filter(
    Post.title.ilike(f"%{search}%")
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

### 정렬

```python
from sqlalchemy import desc, asc

# 내림차순
posts = db.query(Post).order_by(desc(Post.created_at)).all()

# 오름차순
posts = db.query(Post).order_by(asc(Post.title)).all()

# 여러 컬럼
posts = db.query(Post).order_by(
    desc(Post.is_pinned),
    desc(Post.created_at)
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

### Alembic 설정

```bash
# 초기화 (이미 완료됨)
alembic init alembic
```

### 마이그레이션 생성

```bash
# 자동 생성
alembic revision --autogenerate -m "Add users table"

# 수동 생성
alembic revision -m "Add custom migration"
```

### 마이그레이션 적용

```bash
# 최신으로 업그레이드
alembic upgrade head

# 특정 버전으로
alembic upgrade <revision_id>

# 한 단계 다운그레이드
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
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
```

---

## 다음 단계

- [인증](04_authentication.md)
- [CRUD 작업](05_crud.md)

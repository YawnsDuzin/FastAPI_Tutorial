# 수정 및 확장 가이드

이 문서에서는 프로젝트를 수정하고 확장하는 방법을 설명합니다.

## 목차

1. [프로젝트 구조 이해](#프로젝트-구조-이해)
2. [새 모델 추가](#새-모델-추가)
3. [새 API 엔드포인트 추가](#새-api-엔드포인트-추가)
4. [비즈니스 로직 추가](#비즈니스-로직-추가)
5. [인증 커스터마이징](#인증-커스터마이징)
6. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)

---

## 프로젝트 구조 이해

```
app/
├── main.py           # 애플리케이션 진입점
├── config.py         # 설정 관리
├── database.py       # DB 연결
├── models/           # SQLAlchemy 모델 (DB 테이블)
├── schemas/          # Pydantic 스키마 (요청/응답)
├── routers/          # API 라우터 (엔드포인트)
├── services/         # 비즈니스 로직
├── dependencies/     # 종속성 (인증 등)
└── utils/            # 유틸리티 함수
```

### 데이터 흐름

```
Request → Router → Service → Model → Database
                      ↓
Response ← Schema ← Service
```

---

## 새 모델 추가

### 1. 모델 파일 생성

`app/models/product.py`:

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    """상품 모델"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 외래 키 (카테고리와 연결)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    category = relationship("ProductCategory", back_populates="products")
```

### 2. 모델 등록

`app/models/__init__.py`에 추가:

```python
from app.models.product import Product, ProductCategory

__all__ = [
    # ... 기존 모델
    "Product",
    "ProductCategory",
]
```

### 3. 스키마 생성

`app/schemas/product.py`:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

## 새 API 엔드포인트 추가

### 1. 라우터 생성

`app/routers/products.py`:

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.dependencies.auth import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """상품 목록 조회"""
    query = db.query(Product)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 관리자만
):
    """상품 생성 (관리자)"""
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """상품 상세 조회"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="상품을 찾을 수 없습니다."
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """상품 수정 (관리자)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    for field, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """상품 삭제 (관리자)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    db.delete(product)
    db.commit()
```

### 2. 라우터 등록

`app/routers/__init__.py`에 추가:

```python
from app.routers import products  # 추가

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["상품"]
)
```

---

## 비즈니스 로직 추가

### 서비스 레이어 생성

`app/services/product.py`:

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Product]:
        query = self.db.query(Product).filter(Product.is_active == True)

        if category_id:
            query = query.filter(Product.category_id == category_id)
        if min_price:
            query = query.filter(Product.price >= min_price)
        if max_price:
            query = query.filter(Product.price <= max_price)

        return query.offset(skip).limit(limit).all()

    def create_product(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_stock(self, product_id: int, quantity: int) -> Product:
        """재고 업데이트"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

        new_stock = product.stock + quantity
        if new_stock < 0:
            raise HTTPException(status_code=400, detail="재고가 부족합니다.")

        product.stock = new_stock
        self.db.commit()
        self.db.refresh(product)
        return product
```

---

## 인증 커스터마이징

### 새로운 역할 추가

`app/models/user.py`:

```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    SELLER = "seller"      # 새 역할 추가
    USER = "user"
```

### 역할 기반 종속성 추가

`app/dependencies/auth.py`:

```python
def require_seller_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """판매자 또는 관리자만 허용"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="판매자 권한이 필요합니다."
        )
    return current_user
```

### OAuth2 소셜 로그인 추가 예시

```python
# app/routers/auth.py에 추가

@router.get("/google/login")
async def google_login():
    """Google OAuth2 로그인 시작"""
    # OAuth2 라이브러리 사용
    pass

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Google OAuth2 콜백"""
    # 1. code로 토큰 교환
    # 2. 토큰으로 사용자 정보 획득
    # 3. 사용자 생성 또는 조회
    # 4. JWT 토큰 발급
    pass
```

---

## 데이터베이스 마이그레이션

### Alembic 초기화 (이미 완료됨)

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "Add product table"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1

# 현재 버전 확인
alembic current

# 마이그레이션 히스토리
alembic history
```

### 마이그레이션 파일 예시

`alembic/versions/xxx_add_product_table.py`:

```python
def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'])


def downgrade() -> None:
    op.drop_index('ix_products_id', 'products')
    op.drop_table('products')
```

---

## 미들웨어 추가

### 요청 로깅 미들웨어

`app/middleware.py`:

```python
import time
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """요청 로깅 미들웨어"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.4f}s "
        f"status={response.status_code}"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### main.py에 등록

```python
from app.middleware import log_requests

app.middleware("http")(log_requests)
```

---

## 백그라운드 태스크

### 이메일 발송 예시

```python
from fastapi import BackgroundTasks

@router.post("/auth/register")
def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = user_service.create_user(user_data)

    # 백그라운드에서 이메일 발송
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        username=user.username
    )

    return user


def send_verification_email(email: str, username: str):
    """이메일 발송 함수"""
    # 이메일 발송 로직
    pass
```

---

## 테스트 추가

### 새 기능 테스트

`tests/test_products.py`:

```python
import pytest
from fastapi import status


class TestProducts:
    def test_create_product_admin(self, client, admin_headers):
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "테스트 상품",
                "price": 10000,
                "stock": 100
            },
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "테스트 상품"

    def test_create_product_user_forbidden(self, client, auth_headers):
        response = client.post(
            "/api/v1/products/",
            json={"name": "테스트", "price": 1000},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
```

---

## 다음 단계

더 자세한 FastAPI 개념은 튜토리얼 문서를 참조하세요:

- [FastAPI 기본](tutorial/01_fastapi_basics.md)
- [라우팅](tutorial/02_routing.md)
- [데이터베이스](tutorial/03_database.md)
- [인증](tutorial/04_authentication.md)

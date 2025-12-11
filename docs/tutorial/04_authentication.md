# 인증 시스템

이 문서에서는 FastAPI에서 JWT 기반 인증 시스템을 구현하는 방법을 설명합니다.

## 목차

1. [인증 개요](#인증-개요)
2. [비밀번호 해싱](#비밀번호-해싱)
3. [JWT 토큰](#jwt-토큰)
4. [OAuth2 스킴](#oauth2-스킴)
5. [인증 종속성](#인증-종속성)
6. [역할 기반 권한](#역할-기반-권한)

---

## 인증 개요

### 인증 흐름

```
1. 회원가입
   Client → POST /register → Server (비밀번호 해시 → DB 저장)

2. 로그인
   Client → POST /login → Server (비밀번호 검증 → JWT 발급)
        ← {access_token, refresh_token}

3. 인증된 요청
   Client → GET /protected (Authorization: Bearer {token}) → Server
        ← Protected Resource

4. 토큰 갱신
   Client → POST /refresh (refresh_token) → Server
        ← {new_access_token, new_refresh_token}
```

### 필요한 패키지

```txt
# requirements.txt
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # 비밀번호 해싱
python-multipart==0.0.6           # Form 데이터 처리
```

---

## 비밀번호 해싱

### 해싱 유틸리티 (app/utils/security.py)

```python
from passlib.context import CryptContext

# bcrypt 알고리즘 사용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시합니다.

    Args:
        password: 원본 비밀번호

    Returns:
        해시된 비밀번호

    Example:
        hashed = get_password_hash("mypassword123")
        # '$2b$12$...'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호를 검증합니다.

    Args:
        plain_password: 입력된 비밀번호
        hashed_password: 저장된 해시

    Returns:
        일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)
```

### 사용 예시

```python
# 회원가입 시
hashed = get_password_hash("SecureP@ss123")
user = User(email=email, hashed_password=hashed)

# 로그인 시
if verify_password(input_password, user.hashed_password):
    # 인증 성공
else:
    # 인증 실패
```

---

## JWT 토큰

### JWT 구조

```
Header.Payload.Signature

Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": 1, "username": "john", "exp": 1234567890}
Signature: HMAC-SHA256(Header + Payload, secret_key)
```

### 토큰 생성 (app/utils/security.py)

```python
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt, JWTError

from app.config import settings


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id, username 등)
        expires_delta: 만료 시간

    Returns:
        인코딩된 JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """리프레시 토큰 생성"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
```

### 토큰 검증

```python
def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 디코딩

    Args:
        token: JWT 토큰

    Returns:
        디코딩된 페이로드 또는 None (실패 시)
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """토큰 타입 검증"""
    payload = decode_token(token)
    if payload is None:
        return False
    return payload.get("type") == expected_type
```

---

## OAuth2 스킴

### OAuth2PasswordBearer (app/dependencies/auth.py)

```python
from fastapi.security import OAuth2PasswordBearer

# OAuth2 스킴 정의
# tokenUrl: 토큰 발급 엔드포인트
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 선택적 인증 (비로그인도 허용)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False  # 토큰 없어도 에러 안 남
)
```

### 로그인 엔드포인트 (app/routers/auth.py)

```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    로그인

    OAuth2 표준 양식을 사용합니다:
    - Content-Type: application/x-www-form-urlencoded
    - 필드: username, password
    """
    auth_service = AuthService(db)
    return auth_service.login(form_data.username, form_data.password)
```

### AuthService (app/services/auth.py)

```python
class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """사용자 인증"""
        # 이메일 또는 사용자명으로 찾기
        user = self.db.query(User).filter(
            (User.email == username) | (User.username == username)
        ).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def login(self, username: str, password: str) -> Token:
        """로그인 및 토큰 발급"""
        user = self.authenticate_user(username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일/사용자명 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 계정입니다."
            )

        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        self.db.commit()

        # 토큰 생성
        token_data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
```

---

## 인증 종속성

### 현재 사용자 가져오기 (app/dependencies/auth.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 반환

    1. 토큰 디코딩
    2. 토큰 타입 확인
    3. 사용자 조회
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 토큰 디코딩
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # 토큰 타입 확인
    if payload.get("type") != "access":
        raise credentials_exception

    # 사용자 ID 추출
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
```

### 활성 사용자 확인

```python
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """활성화된 사용자만 반환"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다."
        )
    return current_user
```

### 선택적 인증

```python
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적 사용자 반환

    토큰이 없거나 유효하지 않으면 None 반환
    """
    if token is None:
        return None

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return db.query(User).filter(User.id == user_id).first()
```

### 사용 예시

```python
# 인증 필수
@router.get("/profile")
def get_profile(user: User = Depends(get_current_active_user)):
    return user

# 선택적 인증
@router.get("/posts")
def get_posts(
    user: Optional[User] = Depends(get_optional_current_user)
):
    if user:
        # 로그인한 사용자
        include_private = True
    else:
        # 비로그인 사용자
        include_private = False
    # ...
```

---

## 역할 기반 권한

### 역할 정의 (app/models/user.py)

```python
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"          # 관리자
    MODERATOR = "moderator"  # 운영자
    USER = "user"            # 일반 사용자
```

### 관리자 종속성

```python
async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """관리자만 허용"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다. 관리자만 접근할 수 있습니다."
        )
    return current_user
```

### 유연한 역할 체커

```python
def require_role(required_roles: list):
    """
    특정 역할을 요구하는 종속성 팩토리

    Args:
        required_roles: 허용되는 역할 목록

    Returns:
        종속성 함수

    Example:
        @router.get("/admin")
        def admin_only(
            user: User = Depends(require_role([UserRole.ADMIN]))
        ):
            ...

        @router.get("/mod")
        def mod_or_admin(
            user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다."
            )
        return current_user

    return role_checker
```

### 사용 예시

```python
# 관리자 전용
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin_user)
):
    # 관리자만 실행 가능
    pass

# 관리자 또는 운영자
@router.put("/posts/{post_id}/pin")
def pin_post(
    post_id: int,
    user: User = Depends(require_role([UserRole.ADMIN, UserRole.MODERATOR]))
):
    # 관리자 또는 운영자만 게시글 고정 가능
    pass

# 리소스 소유자 또는 관리자
@router.put("/posts/{post_id}")
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    # 작성자 또는 관리자만 수정 가능
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    # 수정 로직
    ...
```

---

## 토큰 갱신

### 갱신 엔드포인트 (app/routers/auth.py)

```python
@router.post("/refresh", response_model=Token)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """리프레시 토큰으로 새 토큰 발급"""
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(request.refresh_token)
```

### 갱신 서비스 (app/services/auth.py)

```python
def refresh_tokens(self, refresh_token: str) -> Token:
    """토큰 갱신"""
    # 토큰 타입 확인
    if not verify_token_type(refresh_token, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다."
        )

    # 토큰 디코딩
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다."
        )

    # 사용자 확인
    user = self.db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

    # 새 토큰 생성
    token_data = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    }

    return Token(
        access_token=create_access_token(data=token_data),
        refresh_token=create_refresh_token(data=token_data),
        token_type="bearer"
    )
```

---

## 다음 단계

- [CRUD 작업](05_crud.md)
- [테스트](06_testing.md)

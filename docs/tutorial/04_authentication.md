# 인증 시스템

이 문서에서는 FastAPI에서 JWT 기반 인증 시스템을 구현하는 방법을 설명합니다.

> **이 문서를 읽기 전에**: [라우팅](02_routing.md)과 [데이터베이스](03_database.md)를 먼저 읽으면 이해가 쉽습니다.

## 인증이란?

> **초보자 안내:** 인증(Authentication)은 **"당신이 정말 그 사람인지 확인하는 과정"**입니다.
>
> 은행에 비유하면:
> ```
> [인증 vs 인가]
>
> 인증 (Authentication): "당신이 누구인지 확인"
>   → 은행에서 신분증 확인
>   → 웹에서 로그인
>
> 인가 (Authorization): "당신이 무엇을 할 수 있는지 확인"
>   → 은행에서 이 계좌의 주인인지 확인
>   → 웹에서 이 게시글을 수정할 권한이 있는지 확인
> ```
>
> **이 프로젝트의 인증 방식:**
> 1. 사용자가 이메일/비밀번호로 로그인
> 2. 서버가 JWT 토큰을 발급
> 3. 사용자가 API 요청할 때마다 토큰을 함께 보냄
> 4. 서버가 토큰을 확인하고 사용자를 식별

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

### 왜 비밀번호를 해시해야 하나요?

> **초보자 안내:** 비밀번호를 **그대로 저장하면 매우 위험**합니다!
>
> ```
> [잘못된 예: 비밀번호 그대로 저장]
>
> users 테이블
> | email          | password     |
> |----------------|--------------|
> | alice@mail.com | mypass123    |  ← 해커가 DB 탈취하면 바로 노출!
> | bob@mail.com   | secret456    |
>
> [올바른 예: 해시로 저장]
>
> users 테이블
> | email          | hashed_password                          |
> |----------------|------------------------------------------|
> | alice@mail.com | $2b$12$LQv3c1yqB...  ← 원래 비밀번호 알 수 없음
> | bob@mail.com   | $2b$12$eUj8P2xK...
> ```
>
> **해시의 특징:**
> - 같은 입력 → 항상 같은 출력
> - 출력 → 입력 역산 불가능 (단방향)
> - 비밀번호 확인: 입력값을 해시해서 저장된 해시와 비교

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

> **초보자 안내:** JWT(JSON Web Token)는 **"디지털 신분증"**과 같습니다.
>
> ```
> [JWT를 왜 사용하나요?]
>
> 전통적인 방식 (세션):
>   사용자 → 로그인 → 서버가 세션 ID 발급 → 서버가 세션 정보 저장
>                                           ↑ 서버가 기억해야 함 (부담)
>
> JWT 방식:
>   사용자 → 로그인 → 서버가 JWT 토큰 발급 → 사용자가 토큰 보관
>                                           ↑ 서버는 기억 안 해도 됨!
>
> JWT 토큰 안에 사용자 정보가 들어있어서,
> 서버는 토큰만 확인하면 누구인지 알 수 있습니다.
> ```
>
> **비유:**
> - 세션 = 놀이공원 입장 후 손목에 도장 (직원이 확인)
> - JWT = 신분증 (신분증 자체에 정보가 있음)

### JWT 구조

```
Header.Payload.Signature

Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": 1, "username": "john", "exp": 1234567890}
Signature: HMAC-SHA256(Header + Payload, secret_key)
```

> **초보자 안내:** JWT는 세 부분으로 구성됩니다:
>
> | 부분 | 역할 | 비유 |
> |------|------|------|
> | Header | 암호화 방식 정보 | 신분증 종류 (주민등록증, 여권 등) |
> | Payload | 실제 데이터 (사용자 ID, 이름 등) | 신분증에 적힌 정보 |
> | Signature | 위조 방지 서명 | 신분증의 홀로그램, 워터마크 |
>
> ```
> eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoiam9obiJ9.abc123...
> └─── Header ────┘ └────────── Payload ───────────────┘ └ Signature ┘
>
> 점(.)으로 구분됩니다. 각 부분은 Base64로 인코딩되어 있어요.
> ```

### Access Token vs Refresh Token

> **초보자 안내:** 왜 토큰이 2개 필요할까요?
>
> ```
> [보안과 편의성의 균형]
>
> Access Token (짧은 수명: 30분~1시간)
>   └─ API 요청할 때 사용
>   └─ 자주 사용하므로 탈취 위험 높음
>   └─ 그래서 수명을 짧게!
>
> Refresh Token (긴 수명: 7일~30일)
>   └─ Access Token 재발급용
>   └─ 자주 사용 안 해서 탈취 위험 낮음
>   └─ 수명 길어도 비교적 안전
>
> [흐름]
> 1. 로그인 → Access Token + Refresh Token 받음
> 2. API 요청 → Access Token 사용
> 3. Access Token 만료 → Refresh Token으로 새 Access Token 발급
> 4. Refresh Token도 만료 → 다시 로그인
> ```
>
> **비유:**
> - Access Token = 일일 출입증 (매일 새로 받음)
> - Refresh Token = 사원증 (분실 전까지 계속 사용)

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

> **초보자 안내:** OAuth2는 **"인증 방식의 표준"**입니다.
>
> ```
> [왜 OAuth2를 사용하나요?]
>
> OAuth2 없이 직접 구현:
>   "우리만의 방식으로 로그인 만들자!"
>   → 보안 허점 발생 가능
>   → 다른 서비스와 호환 안 됨
>   → 문서화 어려움
>
> OAuth2 사용:
>   "검증된 표준 방식을 따르자!"
>   → 보안 검증됨
>   → Swagger UI에서 자동으로 로그인 UI 생성
>   → 다른 서비스와 통합 용이
> ```
>
> **이 프로젝트에서는:**
> - `OAuth2PasswordBearer`: 토큰을 받아서 확인하는 역할
> - `OAuth2PasswordRequestForm`: 로그인 폼 데이터 처리

### OAuth2PasswordBearer (app/dependencies/auth.py)

> **초보자 안내:** `OAuth2PasswordBearer`는 **"토큰 수집기"**입니다.
>
> ```
> [동작 방식]
>
> 클라이언트 요청:
> GET /api/v1/posts
> Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
>                └─────────────────────────────┘
>                   OAuth2PasswordBearer가 이 부분을 추출
>
> → "eyJhbGciOiJIUzI1NiJ9..." 문자열이 함수에 전달됨
> ```

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

> **초보자 안내:** 인증 종속성은 **"경비원"**과 같습니다.
>
> ```
> [인증 종속성의 역할]
>
>                        ┌─────────────┐
> 요청 ──→ [경비원] ──→ │ API 엔드포인트 │
>          (인증 확인)   └─────────────┘
>
> 경비원(종속성)이 하는 일:
> 1. 토큰이 있는지 확인
> 2. 토큰이 유효한지 확인
> 3. 토큰에서 사용자 정보 추출
> 4. 사용자가 활성 상태인지 확인
>
> 모든 확인 통과 → API 실행
> 하나라도 실패 → 401/403 에러
> ```
>
> **장점:**
> - 모든 보호된 API에서 재사용
> - 한 곳에서 인증 로직 관리
> - 테스트 시 쉽게 모킹 가능

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

> **초보자 안내:** 역할 기반 권한은 **"등급별 출입증"**과 같습니다.
>
> ```
> [회사 비유]
>
> ┌─────────────────────────────────────────────────────────┐
> │                        회사 건물                         │
> ├─────────────────────────────────────────────────────────┤
> │  일반 사원 (USER)       ─ 일반 구역만 출입 가능           │
> │  관리자 (MODERATOR)    ─ 일반 + 관리 구역 출입 가능        │
> │  대표이사 (ADMIN)      ─ 모든 구역 출입 가능               │
> └─────────────────────────────────────────────────────────┘
>
> [웹 서비스 비유]
>
> USER:       게시글 읽기/쓰기, 본인 글 수정/삭제
> MODERATOR:  + 다른 사람 글 삭제, 게시글 고정
> ADMIN:      + 사용자 관리, 시스템 설정
> ```
>
> **구현 방식:**
> - 사용자마다 `role` 필드에 역할 저장
> - API 요청 시 역할 확인하는 종속성 사용

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

## 실수하기 쉬운 부분

> **초보자 안내:** 인증 구현 시 흔히 발생하는 실수들입니다.

### 1. 비밀번호를 그대로 저장

```python
# ❌ 잘못된 코드 - 절대 이렇게 하지 마세요!
user = User(email=email, password=password)

# ✅ 올바른 코드
user = User(email=email, hashed_password=get_password_hash(password))
```

### 2. JWT 시크릿 키를 코드에 하드코딩

```python
# ❌ 잘못된 코드
SECRET_KEY = "my-secret-key-123"  # 소스코드에 노출!

# ✅ 올바른 코드 - 환경 변수 사용
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# 또는 settings 사용
from app.config import settings
SECRET_KEY = settings.jwt_secret_key
```

### 3. Access Token과 Refresh Token 혼동

```python
# ❌ 잘못된 코드 - Refresh Token으로 API 호출
# Refresh Token은 토큰 갱신용으로만 사용해야 합니다

# ✅ 올바른 사용법
# - Access Token: API 요청에 사용
# - Refresh Token: /refresh 엔드포인트에만 사용

if payload.get("type") != "access":
    raise HTTPException(status_code=401, detail="Access Token이 필요합니다")
```

### 4. 인증 종속성 빠뜨림

```python
# ❌ 잘못된 코드 - 인증 없이 보호된 데이터 반환
@router.get("/my-profile")
def get_profile(db: Session = Depends(get_db)):
    # 누구의 프로필???
    pass

# ✅ 올바른 코드
@router.get("/my-profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # 인증 필수!
):
    return current_user
```

### 5. 역할 확인 누락

```python
# ❌ 잘못된 코드 - 관리자 기능인데 역할 확인 안 함
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user)  # 로그인만 확인
):
    # 일반 사용자도 다른 사람 삭제 가능! 위험!
    pass

# ✅ 올바른 코드
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user)  # 관리자만!
):
    pass
```

---

## 요약

| 개념 | 설명 | 파일 |
|------|------|------|
| 비밀번호 해싱 | bcrypt로 안전하게 저장 | `app/utils/security.py` |
| JWT 토큰 | 사용자 인증 정보 담은 토큰 | `app/utils/security.py` |
| OAuth2 스킴 | 표준 인증 방식 | `app/dependencies/auth.py` |
| 인증 종속성 | 사용자 확인하는 경비원 | `app/dependencies/auth.py` |
| 역할 기반 권한 | 등급별 기능 제한 | `app/dependencies/auth.py` |

---

## 다음 단계

인증 시스템을 이해했다면:

- **[CRUD 작업](05_crud.md)**: 인증된 사용자로 데이터 생성/조회/수정/삭제하기
- **[테스트](06_testing.md)**: 인증이 필요한 API 테스트 작성하기

> **팁:** CRUD 작업에서 인증과 권한이 실제로 어떻게 사용되는지 확인할 수 있습니다.

# 테스트

이 문서에서는 FastAPI 애플리케이션을 테스트하는 방법을 설명합니다.

> **이 문서를 읽기 전에**: [CRUD 작업](05_crud.md)과 [인증](04_authentication.md)을 먼저 읽으면 이해가 쉽습니다.

## 테스트란?

> **초보자 안내:** 테스트는 **"코드가 제대로 작동하는지 자동으로 확인하는 것"**입니다.
>
> ```
> [테스트 없이 개발]
>
> 코드 수정 → Swagger에서 직접 테스트 → 되는 것 같음 → 배포
>                                                      ↓
>                              "어? 로그인이 안 돼요!" (다른 기능 고장)
>
> [테스트 있는 개발]
>
> 코드 수정 → pytest 실행 → 3개 테스트 실패 발견 → 수정 → 배포
>                              ↓
>                "로그인 테스트가 실패했네? 고치자"
> ```
>
> **왜 테스트가 필요한가요?**
>
> | 이유 | 설명 |
> |------|------|
> | **버그 예방** | 새 기능 추가할 때 기존 기능이 깨지는지 확인 |
> | **리팩토링 안전** | 코드 구조 바꿔도 기능은 그대로인지 확인 |
> | **문서 역할** | 테스트 코드가 "이렇게 동작해야 함"을 보여줌 |
> | **자신감** | 배포할 때 "잘 될 거야" 대신 "테스트 통과했어" |
>
> **테스트의 종류:**
> ```
> ┌─────────────────────────────────────────────┐
> │           E2E (End-to-End) 테스트            │  ← 가장 느림, 적게
> │     실제 브라우저로 전체 흐름 테스트           │
> ├─────────────────────────────────────────────┤
> │              통합 (Integration) 테스트        │
> │        API 엔드포인트 전체 동작 테스트         │
> ├─────────────────────────────────────────────┤
> │                 단위 (Unit) 테스트            │  ← 가장 빠름, 많이
> │            함수/메서드 하나씩 테스트           │
> └─────────────────────────────────────────────┘
>
> 이 프로젝트에서는 주로 API 통합 테스트와 서비스 단위 테스트를 다룹니다.
> ```

## 목차

1. [테스트 환경 설정](#테스트-환경-설정)
2. [Fixture 작성](#fixture-작성)
3. [API 테스트](#api-테스트)
4. [인증 테스트](#인증-테스트)
5. [서비스 테스트](#서비스-테스트)
6. [테스트 실행](#테스트-실행)

---

## 테스트 환경 설정

> **초보자 안내:** 테스트 환경은 **"실제 서비스에 영향 없이 테스트할 수 있는 별도 공간"**입니다.
>
> ```
> [왜 별도 환경이 필요한가요?]
>
> 실제 DB로 테스트하면:
>   - 테스트 데이터가 실제 데이터와 섞임
>   - 테스트에서 삭제한 데이터가 진짜 삭제됨
>   - 테스트 실패 시 DB 상태가 엉망이 됨
>
> 테스트용 인메모리 DB 사용:
>   - 메모리에만 존재 (파일 없음)
>   - 테스트 끝나면 자동으로 사라짐
>   - 매 테스트마다 깨끗한 상태에서 시작
> ```

### 필요한 패키지

```txt
# requirements.txt
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

> **초보자 안내:**
> - **pytest**: Python 표준 테스트 프레임워크
> - **pytest-asyncio**: 비동기 함수 테스트용
> - **httpx**: HTTP 클라이언트 (TestClient 내부에서 사용)

### 테스트 구조

```
tests/
├── __init__.py
├── conftest.py      # 공통 fixture (테스트 준비물)
├── test_auth.py     # 인증 테스트
├── test_posts.py    # 게시글 테스트
├── test_users.py    # 사용자 테스트
└── test_services/   # 서비스 단위 테스트
```

> **초보자 안내:**
> - 파일 이름은 반드시 `test_`로 시작해야 pytest가 인식합니다
> - `conftest.py`는 특별한 파일로, 여기의 fixture는 모든 테스트에서 사용 가능

---

## Fixture 작성

> **초보자 안내:** Fixture는 **"테스트에 필요한 준비물"**입니다.
>
> ```
> [Fixture 없이]
>
> def test_게시글_조회():
>     # 매번 사용자 만들고...
>     user = User(email="test@example.com", ...)
>     db.add(user)
>     db.commit()
>     # 매번 로그인하고...
>     token = login(user)
>     # 매번 게시글 만들고...
>     post = Post(title="테스트", author_id=user.id)
>     db.add(post)
>     db.commit()
>     # 이제야 테스트...
>     response = client.get(f"/posts/{post.id}")
>
> [Fixture 사용]
>
> def test_게시글_조회(client, auth_headers, test_post):
>     # 준비물이 자동으로 제공됨!
>     response = client.get(f"/posts/{test_post.id}", headers=auth_headers)
>
> Fixture가 필요한 준비를 대신 해줍니다.
> ```
>
> **Fixture의 장점:**
> - 중복 코드 제거
> - 테스트 코드가 간결해짐
> - 준비 로직을 한 곳에서 관리

### conftest.py (tests/conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


# 테스트용 인메모리 SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    """테스트용 DB 세션"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 의존성 오버라이드
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """
    각 테스트마다 새로운 DB 세션

    테스트 전: 테이블 생성
    테스트 후: 테이블 삭제
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """테스트용 FastAPI 클라이언트"""
    with TestClient(app) as c:
        yield c
```

### 사용자 Fixture

```python
@pytest.fixture(scope="function")
def test_user(db_session) -> User:
    """테스트용 일반 사용자"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(db_session) -> User:
    """테스트용 관리자"""
    user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=get_password_hash("AdminPass123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

### 인증 토큰 Fixture

```python
@pytest.fixture(scope="function")
def user_token(client, test_user):
    """일반 사용자 토큰"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """관리자 토큰"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "adminuser",
            "password": "AdminPass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(user_token):
    """일반 사용자 인증 헤더"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    """관리자 인증 헤더"""
    return {"Authorization": f"Bearer {admin_token}"}
```

---

## API 테스트

> **초보자 안내:** API 테스트는 **"실제 API 호출처럼 테스트"**하는 것입니다.
>
> ```
> [TestClient 동작 방식]
>
>                      테스트 코드
>                          │
>           client.get("/api/v1/posts/1")
>                          │
>                          ▼
>                   ┌──────────────┐
>                   │  TestClient  │ ← 실제 HTTP 대신 직접 호출
>                   └──────────────┘
>                          │
>                          ▼
>                   ┌──────────────┐
>                   │   FastAPI    │
>                   │     App      │
>                   └──────────────┘
>                          │
>                          ▼
>                      Response
>
> 실제 서버를 띄우지 않고도 API를 테스트할 수 있습니다!
> ```
>
> **테스트 시 확인할 것:**
> - 상태 코드 (200, 201, 400, 401, 404 등)
> - 응답 본문 (JSON 데이터)
> - 에러 메시지

### 기본 테스트 패턴

```python
from fastapi import status


class TestEndpoint:
    """엔드포인트 테스트 클래스"""

    def test_success_case(self, client, auth_headers):
        """성공 케이스"""
        response = client.get("/api/v1/endpoint", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert "expected_field" in response.json()

    def test_unauthorized(self, client):
        """인증 없이 접근"""
        response = client.get("/api/v1/protected")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_not_found(self, client, auth_headers):
        """존재하지 않는 리소스"""
        response = client.get("/api/v1/items/99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
```

### 프로젝트 예시 (tests/test_auth.py)

```python
import pytest
from fastapi import status


class TestRegister:
    """회원가입 테스트"""

    def test_register_success(self, client):
        """정상 회원가입"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewPass123",
                "full_name": "New User"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data  # 비밀번호는 응답에 없어야 함

    def test_register_duplicate_email(self, client, test_user):
        """이메일 중복"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # 이미 존재
                "username": "anotheruser",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "이미 등록된 이메일" in response.json()["detail"]

    def test_register_weak_password(self, client):
        """약한 비밀번호"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "weak"  # 요구사항 미충족
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """로그인 테스트"""

    def test_login_with_email(self, client, test_user):
        """이메일로 로그인"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_username(self, client, test_user):
        """사용자명으로 로그인"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_200_OK

    def test_login_wrong_password(self, client, test_user):
        """잘못된 비밀번호"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "WrongPassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

---

## 인증 테스트

### 토큰 테스트

```python
class TestTokenRefresh:
    """토큰 갱신 테스트"""

    def test_refresh_success(self, client, test_user):
        """토큰 갱신 성공"""
        # 로그인
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "TestPass123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # 갱신
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, client):
        """유효하지 않은 토큰"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoints:
    """보호된 엔드포인트 테스트"""

    def test_get_me_success(self, client, auth_headers):
        """내 정보 조회 성공"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "testuser"

    def test_get_me_unauthorized(self, client):
        """인증 없이 접근"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_only_endpoint(self, client, auth_headers):
        """관리자 전용 엔드포인트에 일반 사용자 접근"""
        response = client.get(
            "/api/v1/users/",  # 관리자 전용
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_endpoint_success(self, client, admin_headers):
        """관리자가 관리자 전용 엔드포인트 접근"""
        response = client.get(
            "/api/v1/users/",
            headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
```

---

## 서비스 테스트

### 단위 테스트

```python
# tests/test_services/test_user_service.py

import pytest
from app.services.user import UserService
from app.schemas.user import UserCreate


class TestUserService:
    """UserService 단위 테스트"""

    def test_create_user(self, db_session):
        """사용자 생성"""
        service = UserService(db_session)

        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            password="SecurePass123"
        )

        user = service.create_user(user_data)

        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        # 비밀번호는 해시되어야 함
        assert user.hashed_password != "SecurePass123"

    def test_get_user(self, db_session, test_user):
        """사용자 조회"""
        service = UserService(db_session)

        user = service.get_user(test_user.id)

        assert user is not None
        assert user.id == test_user.id

    def test_get_user_not_found(self, db_session):
        """존재하지 않는 사용자 조회"""
        service = UserService(db_session)

        user = service.get_user(99999)

        assert user is None
```

---

## 테스트 실행

### 기본 실행

```bash
# 모든 테스트 실행
pytest

# 상세 출력
pytest -v

# 특정 파일
pytest tests/test_auth.py

# 특정 클래스
pytest tests/test_auth.py::TestLogin

# 특정 테스트
pytest tests/test_auth.py::TestLogin::test_login_success
```

### 유용한 옵션

```bash
# 실패 시 즉시 중단
pytest -x

# 마지막 실패한 테스트만
pytest --lf

# 커버리지
pytest --cov=app --cov-report=html

# 경고 표시
pytest -W default

# 병렬 실행 (pytest-xdist 필요)
pytest -n auto
```

### pytest.ini 설정

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

### 테스트 커버리지 확인

```bash
# 커버리지 설치
pip install pytest-cov

# 커버리지 실행
pytest --cov=app --cov-report=term-missing

# HTML 리포트 생성
pytest --cov=app --cov-report=html
# htmlcov/index.html 확인
```

---

## 모킹(Mocking)

### 외부 서비스 모킹

```python
from unittest.mock import patch, MagicMock


class TestEmailService:
    """이메일 서비스 테스트"""

    @patch("app.services.email.send_email")
    def test_send_verification_email(self, mock_send, client):
        """이메일 발송 모킹"""
        mock_send.return_value = True

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "TestPass123"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_send.assert_called_once()
```

### 데이터베이스 모킹

```python
from unittest.mock import MagicMock


def test_with_mock_db():
    """DB 세션 모킹"""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    service = UserService(mock_db)
    result = service.get_user(1)

    assert result is None
    mock_db.query.assert_called_once()
```

---

## 테스트 모범 사례

1. **각 테스트는 독립적으로**: 다른 테스트에 의존하지 않음
2. **한 테스트, 한 개념**: 하나의 동작만 테스트
3. **명확한 이름**: `test_[무엇을]_[어떤 상황에서]_[예상 결과]`
4. **AAA 패턴**: Arrange(준비), Act(실행), Assert(검증)
5. **경계 조건 테스트**: 빈 값, 최대값, 잘못된 타입 등

```python
def test_create_post_with_empty_title_should_fail(self, client, auth_headers):
    """빈 제목으로 게시글 생성 시 실패해야 함"""
    # Arrange
    post_data = {"title": "", "content": "내용"}

    # Act
    response = client.post(
        "/api/v1/posts/",
        json=post_data,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

---

## 실수하기 쉬운 부분

> **초보자 안내:** 테스트 작성 시 흔히 발생하는 실수들입니다.

### 1. DB 변경사항이 다른 테스트에 영향

```python
# ❌ 잘못된 방식 - 테이블 초기화 안 함
@pytest.fixture(scope="session")  # 세션 동안 한 번만 실행
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # 테이블 삭제 안 함 → 이전 테스트 데이터가 남아있음

# ✅ 올바른 방식 - 테스트마다 초기화
@pytest.fixture(scope="function")  # 테스트마다 실행
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # 테스트 후 정리
```

### 2. 테스트 순서에 의존

```python
# ❌ 잘못된 코드 - 다른 테스트에서 만든 데이터에 의존
def test_첫번째():
    client.post("/posts", json={"title": "테스트"})

def test_두번째():
    # test_첫번째에서 만든 게시글이 있다고 가정
    response = client.get("/posts/1")  # 순서 바뀌면 실패!
    assert response.status_code == 200

# ✅ 올바른 코드 - 각 테스트가 독립적
def test_게시글_조회(test_post):  # fixture로 준비
    response = client.get(f"/posts/{test_post.id}")
    assert response.status_code == 200
```

### 3. 하드코딩된 ID 사용

```python
# ❌ 잘못된 코드
def test_사용자_조회():
    response = client.get("/users/1")  # 1번 사용자가 있다고 가정?

# ✅ 올바른 코드
def test_사용자_조회(test_user):
    response = client.get(f"/users/{test_user.id}")  # 동적 ID 사용
```

### 4. 인증 헤더 빠뜨림

```python
# ❌ 잘못된 코드 - 401 에러 발생
def test_내_게시글_조회(client):
    response = client.get("/posts/my")  # 인증 헤더 없음!
    assert response.status_code == 200  # 실패

# ✅ 올바른 코드
def test_내_게시글_조회(client, auth_headers):
    response = client.get("/posts/my", headers=auth_headers)
    assert response.status_code == 200
```

### 5. 에러 케이스 테스트 안 함

```python
# ❌ 성공 케이스만 테스트
def test_로그인():
    response = client.post("/login", data={"username": "test", "password": "pass"})
    assert response.status_code == 200

# ✅ 실패 케이스도 테스트
def test_로그인_성공(client, test_user):
    response = client.post("/login", data={"username": "test", "password": "pass"})
    assert response.status_code == 200

def test_로그인_잘못된_비밀번호(client, test_user):
    response = client.post("/login", data={"username": "test", "password": "wrong"})
    assert response.status_code == 401

def test_로그인_존재하지않는_사용자(client):
    response = client.post("/login", data={"username": "nobody", "password": "pass"})
    assert response.status_code == 401
```

---

## 요약

| 개념 | 설명 |
|------|------|
| **pytest** | Python 테스트 프레임워크 |
| **Fixture** | 테스트 준비물 (@pytest.fixture) |
| **TestClient** | FastAPI 테스트용 HTTP 클라이언트 |
| **인메모리 DB** | 테스트용 임시 데이터베이스 |
| **AAA 패턴** | Arrange(준비) → Act(실행) → Assert(검증) |
| **Mocking** | 외부 서비스를 가짜로 대체 |

---

## 다음 단계

테스트를 이해했다면 이 튜토리얼을 마쳤습니다! 🎉

### 더 공부할 내용

- **[API 레퍼런스](../04_api_reference.md)**: 모든 API 엔드포인트 상세 문서
- **[수정 및 확장 가이드](../05_customization.md)**: 프로젝트 커스터마이징 방법

### 추천 학습 경로

```
1. 이 프로젝트 실행해보기
   └─ 로컬에서 서버 실행, Swagger로 API 테스트

2. 간단한 기능 추가해보기
   └─ 새 모델 추가, CRUD API 만들기

3. 테스트 작성해보기
   └─ 추가한 기능에 대한 테스트 작성

4. 자신만의 프로젝트 시작
   └─ 이 보일러플레이트를 기반으로 새 프로젝트
```

### 유용한 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/ko/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [pytest 문서](https://docs.pytest.org/)
- [Pydantic 문서](https://docs.pydantic.dev/)

> **팁:** 가장 좋은 학습 방법은 직접 코드를 작성해보는 것입니다. 이 프로젝트를 fork해서 자유롭게 실험해보세요!

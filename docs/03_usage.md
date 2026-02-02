# 사용 가이드

이 문서에서는 API 사용 방법을 단계별로 설명합니다.

> **초보자 안내:** 이 문서는 서버가 이미 실행 중인 상태를 전제로 합니다.
> 아직 서버를 실행하지 않았다면 [설치 가이드](01_installation.md)를 먼저 따라해주세요.

## 목차

1. [시작하기](#시작하기)
2. [Swagger UI 사용법 (초보자 필독!)](#swagger-ui-사용법)
3. [인증](#인증)
4. [사용자 관리](#사용자-관리)
5. [게시판](#게시판)
6. [대시보드](#대시보드)
7. [테마 설정](#테마-설정)
8. [메뉴 관리](#메뉴-관리)
9. [HTTP 상태 코드](#http-상태-코드)

---

## 시작하기

### API 기본 URL

```
http://localhost:8000/api/v1
```

> **URL 구조 설명:**
> - `http://localhost:8000`: 내 컴퓨터에서 돌아가는 서버 주소
> - `/api/v1`: API 경로의 접두사 (버전 1이라는 뜻)
> - 예: `/api/v1/posts/` → 게시글 관련 API

### API 문서 확인

- **Swagger UI**: http://localhost:8000/docs (API를 직접 테스트할 수 있는 화면)
- **ReDoc**: http://localhost:8000/redoc (읽기 편한 API 문서)

### 헬스 체크

서버가 정상 작동하는지 확인하는 가장 간단한 방법입니다.

**브라우저에서 확인:**
http://localhost:8000/health 에 접속

**또는 터미널에서:**
```bash
curl http://localhost:8000/health
```

응답:
```json
{
    "status": "healthy",
    "database": "sqlite"
}
```

> **curl이란?** 터미널에서 HTTP 요청을 보내는 도구입니다.
> 브라우저 없이 API를 테스트할 때 사용합니다.
> 아래 예시들은 모두 curl로 작성되어 있지만, Swagger UI에서도 동일하게 테스트할 수 있습니다.

---

## Swagger UI 사용법

> **Swagger UI는 FastAPI가 자동으로 만들어주는 API 테스트 도구입니다.**
> curl 명령어를 외울 필요 없이, 웹 브라우저에서 버튼 클릭만으로 모든 API를 테스트할 수 있습니다.
> **초보자에게 가장 추천하는 방법입니다!**

### 접속 방법

1. 서버를 실행합니다: `uvicorn app.main:app --reload`
2. 브라우저에서 **http://localhost:8000/docs** 접속

### 화면 구성

```
┌──────────────────────────────────────────────┐
│  FastAPI Boilerplate                          │
│                                              │
│  ▼ 인증                                      │ ← 카테고리 (태그)
│    POST /api/v1/auth/register  회원가입       │ ← 각 API 엔드포인트
│    POST /api/v1/auth/login     로그인         │
│    POST /api/v1/auth/refresh   토큰 갱신      │
│    GET  /api/v1/auth/me        내 정보        │
│                                              │
│  ▼ 게시판                                     │
│    GET  /api/v1/posts/         게시글 목록     │
│    POST /api/v1/posts/         게시글 작성     │
│    ...                                       │
│                                              │
│  ▼ 사용자                                     │
│    ...                                       │
└──────────────────────────────────────────────┘
```

### API 테스트하는 법 (단계별)

#### 1단계: 회원가입 해보기

1. **`POST /api/v1/auth/register`** 를 클릭하여 펼침
2. 오른쪽의 **"Try it out"** 버튼 클릭
3. Request body에 다음 내용을 입력:

```json
{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123",
    "full_name": "테스트 사용자"
}
```

4. **"Execute"** 버튼 클릭
5. 아래에 응답 결과가 나타남

```
┌─────────────────────────────────────────┐
│  Responses                              │
│  Code: 201                              │ ← 성공! (201 = 생성됨)
│  Response body:                         │
│  {                                      │
│    "id": 1,                             │
│    "email": "test@example.com",         │
│    "username": "testuser",              │
│    "role": "user",                      │
│    "is_active": true                    │
│  }                                      │
└─────────────────────────────────────────┘
```

#### 2단계: 로그인하기

1. **`POST /api/v1/auth/login`** 을 클릭하여 펼침
2. **"Try it out"** 클릭
3. 로그인은 Form 형식이므로 각 필드를 입력:
   - username: `test@example.com` (또는 `testuser`)
   - password: `TestPass123`
4. **"Execute"** 클릭
5. 응답에서 `access_token` 값을 복사

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

#### 3단계: 인증이 필요한 API 사용하기 (토큰 설정)

1. 페이지 맨 위의 **"Authorize"** 버튼 클릭 (자물쇠 아이콘)
2. Value 입력란에 복사한 토큰을 붙여넣기
3. **"Authorize"** 클릭 → **"Close"** 클릭

이제 인증이 필요한 모든 API를 테스트할 수 있습니다!

```
┌─────────────────────────────────┐
│  Available authorizations        │
│                                 │
│  OAuth2PasswordBearer (OAuth2)  │
│  Value: eyJhbGciOiJIUzI1NiIs.. │ ← 토큰 붙여넣기
│                                 │
│  [Authorize]  [Close]           │
└─────────────────────────────────┘
```

#### 4단계: 게시글 작성해보기

1. **`POST /api/v1/posts/`** 클릭
2. **"Try it out"** 클릭
3. Request body 입력:

```json
{
    "title": "나의 첫 게시글",
    "content": "FastAPI로 만든 첫 게시글입니다!",
    "is_published": true
}
```

4. **"Execute"** 클릭
5. 201 응답이 나오면 성공!

> **팁:** Swagger UI에서 각 API 옆의 자물쇠 아이콘이 있으면
> 인증이 필요한 API라는 뜻입니다. 먼저 Authorize를 해야 합니다.

---

## 인증

### 회원가입

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "SecurePass123",
    "full_name": "홍길동"
  }'
```

> **명령어 설명:**
> - `curl -X POST`: POST 방식으로 요청 보내기
> - `-H "Content-Type: application/json"`: "JSON 형식으로 보낼게요"라고 알림
> - `-d '{...}'`: 보내는 데이터 (회원 정보)
>
> **비밀번호 요구사항:**
> - 8자 이상
> - 대문자 포함 (예: S, P)
> - 숫자 포함 (예: 1, 2, 3)

응답:
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "myuser",
    "full_name": "홍길동",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00"
}
```

### 로그인

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123"
```

> **왜 로그인만 형식이 다른가요?**
> 로그인은 OAuth2 표준을 따르기 때문에 JSON이 아닌 Form 형식(`application/x-www-form-urlencoded`)을 사용합니다.
> 이것은 보안 표준 규격에 따른 것입니다.

응답:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

> **응답 설명:**
> - `access_token`: API를 호출할 때 사용하는 토큰 (유효기간: 30분)
> - `refresh_token`: 액세스 토큰이 만료되었을 때 새로 발급받는 데 사용 (유효기간: 7일)
> - `token_type`: "bearer" = "이 토큰을 가진 사람"이라는 뜻

### 토큰 사용

모든 인증이 필요한 API 호출에 토큰을 포함합니다:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

> **이 헤더의 의미:**
> `Authorization: Bearer 토큰값`
> → "나는 이 토큰을 가진 사용자예요"라고 서버에 알려주는 것

### 토큰 갱신

액세스 토큰이 만료되면 리프레시 토큰으로 새 토큰을 발급받습니다:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

> **언제 이걸 사용하나요?**
> API를 호출했는데 401(인증 실패) 에러가 나면, 액세스 토큰이 만료된 것입니다.
> 이때 리프레시 토큰으로 새 토큰을 받으면 다시 로그인하지 않아도 됩니다.
>
> ```
> 일반적인 흐름:
> 1. 로그인 → access_token, refresh_token 받음
> 2. API 호출 시 access_token 사용
> 3. 30분 후 access_token 만료 → 401 에러 발생
> 4. refresh_token으로 새 access_token 발급
> 5. 새 access_token으로 API 호출 재시도
> 6. refresh_token도 만료되면 (7일 후) → 다시 로그인
> ```

---

## 사용자 관리

### 내 정보 조회

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {token}"
```

> `{token}` 부분을 로그인 시 받은 실제 토큰 값으로 교체하세요.

### 내 정보 수정

```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "김철수",
    "email": "newemail@example.com"
  }'
```

### 비밀번호 변경

```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewSecurePass456"
  }'
```

### 사용자 목록 조회 (관리자만)

```bash
curl "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer {admin_token}"
```

> **`?skip=0&limit=10` 란?**
> URL 뒤에 `?`로 시작하는 부분은 **쿼리 매개변수**입니다.
> - `skip=0`: 0개를 건너뛰고 (처음부터)
> - `limit=10`: 10개만 가져오기
> - 이것이 **페이지네이션**의 기본 원리입니다

---

## 게시판

### 게시글 목록 조회

```bash
# 기본 조회
curl http://localhost:8000/api/v1/posts/

# 페이지네이션 (2페이지, 페이지당 10개)
curl "http://localhost:8000/api/v1/posts/?page=2&size=10"

# 검색 (제목이나 내용에 "FastAPI"가 포함된 글)
curl "http://localhost:8000/api/v1/posts/?search=FastAPI"

# 카테고리 필터 (1번 카테고리의 글만)
curl "http://localhost:8000/api/v1/posts/?category_id=1"

# 조합 (1번 카테고리에서 "FastAPI" 검색, 1페이지)
curl "http://localhost:8000/api/v1/posts/?category_id=1&search=FastAPI&page=1&size=10"
```

응답:
```json
{
    "items": [
        {
            "id": 1,
            "title": "FastAPI 시작하기",
            "content": "FastAPI는...",
            "slug": "fastapi-시작하기-1",
            "view_count": 100,
            "author": {
                "id": 1,
                "username": "admin"
            },
            "created_at": "2024-01-01T00:00:00"
        }
    ],
    "total": 50,
    "page": 1,
    "size": 10,
    "pages": 5
}
```

> **응답 구조 설명:**
> - `items`: 게시글 목록 (배열)
> - `total`: 전체 게시글 수 (검색/필터 결과 포함)
> - `page`: 현재 페이지 번호
> - `size`: 페이지당 표시 개수
> - `pages`: 전체 페이지 수 (total / size)

### 게시글 작성 (로그인 필요)

```bash
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "새 게시글",
    "content": "게시글 내용입니다.",
    "category_id": 1,
    "is_published": true
  }'
```

> **`is_published`란?**
> - `true`: 다른 사람에게 공개됨
> - `false`: 임시저장 (작성자와 관리자만 볼 수 있음)

### 게시글 상세 조회

```bash
curl http://localhost:8000/api/v1/posts/1
```

> 조회할 때마다 `view_count`(조회수)가 자동으로 1 증가합니다.

### 게시글 수정 (작성자 또는 관리자만)

```bash
curl -X PUT http://localhost:8000/api/v1/posts/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "수정된 제목",
    "content": "수정된 내용"
  }'
```

> 변경하고 싶은 필드만 보내면 됩니다. 예를 들어 제목만 바꾸고 싶으면:
> ```json
> {"title": "새로운 제목"}
> ```

### 게시글 삭제 (작성자 또는 관리자만)

```bash
curl -X DELETE http://localhost:8000/api/v1/posts/1 \
  -H "Authorization: Bearer {token}"
```

> 삭제 성공 시 204(No Content) 응답이 돌아옵니다. 본문은 비어있습니다.

### 댓글 작성

```bash
curl -X POST http://localhost:8000/api/v1/posts/1/comments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "좋은 글입니다!"
  }'
```

### 대댓글 작성

```bash
curl -X POST http://localhost:8000/api/v1/posts/1/comments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "감사합니다!",
    "parent_id": 1
  }'
```

> **`parent_id`란?** 어떤 댓글에 대한 답글인지를 지정합니다.
> `parent_id: 1` = 1번 댓글에 대한 답글

### 댓글 목록 조회

```bash
curl http://localhost:8000/api/v1/posts/1/comments
```

---

## 대시보드

### 통계 조회

```bash
curl http://localhost:8000/api/v1/dashboard/ \
  -H "Authorization: Bearer {token}"
```

응답:
```json
{
    "total_posts": 150,
    "total_users": 50,
    "total_comments": 320,
    "posts_today": 5,
    "users_today": 2,
    "my_posts": 10,
    "my_comments": 25
}
```

> **각 필드 설명:**
> | 필드 | 의미 |
> |------|------|
> | `total_posts` | 전체 게시글 수 |
> | `total_users` | 전체 사용자 수 |
> | `total_comments` | 전체 댓글 수 |
> | `posts_today` | 오늘 작성된 게시글 수 |
> | `users_today` | 오늘 가입한 사용자 수 |
> | `my_posts` | 내가 작성한 게시글 수 |
> | `my_comments` | 내가 작성한 댓글 수 |

### 관리자 통계 (관리자)

```bash
curl http://localhost:8000/api/v1/dashboard/admin \
  -H "Authorization: Bearer {admin_token}"
```

### 최근 게시글

```bash
curl "http://localhost:8000/api/v1/dashboard/recent-posts?limit=5" \
  -H "Authorization: Bearer {token}"
```

### 최근 가입자 (관리자)

```bash
curl "http://localhost:8000/api/v1/dashboard/recent-users?limit=5" \
  -H "Authorization: Bearer {admin_token}"
```

---

## 테마 설정

### 사용 가능한 테마 조회

```bash
curl http://localhost:8000/api/v1/theme/available
```

응답:
```json
{
    "themes": ["light", "dark", "blue", "green"],
    "default_theme": "light"
}
```

### 내 테마 설정 조회

```bash
curl http://localhost:8000/api/v1/theme/ \
  -H "Authorization: Bearer {token}"
```

### 테마 설정 변경

```bash
curl -X PUT http://localhost:8000/api/v1/theme/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "theme_name": "dark",
    "sidebar_collapsed": true,
    "custom_settings": {
        "font_size": "large",
        "language": "ko"
    }
  }'
```

---

## 메뉴 관리

### 메뉴 트리 조회

```bash
# 비로그인 (공개 메뉴만)
curl http://localhost:8000/api/v1/menu/

# 로그인 (역할에 따른 메뉴)
curl http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer {token}"
```

> **역할에 따른 메뉴란?**
> 관리자만 볼 수 있는 메뉴(예: 사용자 관리)는 일반 사용자에게 표시되지 않습니다.

응답:
```json
{
    "menus": [
        {
            "id": 1,
            "name": "대시보드",
            "url": "/dashboard",
            "icon": "fa-dashboard",
            "children": []
        },
        {
            "id": 2,
            "name": "게시판",
            "url": "/posts",
            "icon": "fa-list",
            "children": [
                {
                    "id": 3,
                    "name": "공지사항",
                    "url": "/posts/notices"
                }
            ]
        }
    ]
}
```

> **`children`이란?** 하위 메뉴 목록입니다. 메뉴가 트리(나무) 구조로 되어 있어서
> 상위 메뉴 아래에 하위 메뉴가 들어갈 수 있습니다.

### 기본 메뉴 초기화 (관리자)

```bash
curl -X POST http://localhost:8000/api/v1/menu/init-default \
  -H "Authorization: Bearer {admin_token}"
```

### 메뉴 생성 (관리자)

```bash
curl -X POST http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "새 메뉴",
    "url": "/new-menu",
    "icon": "fa-star",
    "order": 5
  }'
```

### 하위 메뉴 생성 (관리자)

```bash
curl -X POST http://localhost:8000/api/v1/menu/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "하위 메뉴",
    "url": "/parent/child",
    "parent_id": 1,
    "order": 0
  }'
```

### 메뉴 수정 (관리자)

```bash
curl -X PUT http://localhost:8000/api/v1/menu/1 \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "수정된 메뉴",
    "is_active": false
  }'
```

### 메뉴 삭제 (관리자)

```bash
curl -X DELETE http://localhost:8000/api/v1/menu/1 \
  -H "Authorization: Bearer {admin_token}"
```

---

## HTTP 상태 코드

서버의 응답에 포함되는 숫자 코드입니다. 요청이 어떻게 처리되었는지를 알려줍니다.

### 성공 (2xx)

| 코드 | 이름 | 의미 | 쉬운 설명 |
|------|------|------|----------|
| **200** | OK | 성공 | "잘 됐어요!" |
| **201** | Created | 생성 성공 | "새로 만들었어요!" |
| **204** | No Content | 삭제 성공 | "지웠어요! (돌려줄 건 없어요)" |

### 클라이언트 에러 (4xx) - 요청하는 쪽의 문제

| 코드 | 이름 | 의미 | 쉬운 설명 |
|------|------|------|----------|
| **400** | Bad Request | 잘못된 요청 | "보내신 데이터가 이상해요" |
| **401** | Unauthorized | 인증 필요 | "로그인 먼저 해주세요" |
| **403** | Forbidden | 권한 없음 | "로그인은 했지만 이건 못 해요" |
| **404** | Not Found | 찾을 수 없음 | "그런 거 없는데요?" |
| **422** | Unprocessable | 검증 실패 | "형식은 맞는데 내용이 틀려요" |

### 서버 에러 (5xx)

| 코드 | 이름 | 의미 | 쉬운 설명 |
|------|------|------|----------|
| **500** | Server Error | 서버 오류 | "서버에 문제가 생겼어요 (우리 잘못)" |

### 자주 만나는 에러와 해결법

| 에러 코드 | 원인 | 해결 방법 |
|----------|------|---------|
| 401 | 토큰이 없거나 만료됨 | 다시 로그인하거나 토큰 갱신 |
| 403 | 권한이 없는 작업 | 관리자 계정으로 시도 |
| 404 | 없는 게시글/사용자 요청 | ID를 확인 |
| 422 | 필수 필드 누락 또는 형식 오류 | 요청 데이터 확인 |

---

## 다음 단계

- [API 레퍼런스](04_api_reference.md): 전체 API 상세 문서
- [수정 및 확장](05_customization.md): 커스터마이징 가이드

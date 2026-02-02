# 시작하기 전에 - 개발 환경 준비

> 이 문서는 FastAPI 프로젝트를 시작하기 전에 필요한 기본 도구와 지식을 안내합니다.
> 이미 Python 개발 경험이 있다면 [설치 가이드](../01_installation.md)로 건너뛰어도 됩니다.

## 목차

1. [필요한 기본 지식](#필요한-기본-지식)
2. [Python 설치하기](#python-설치하기)
3. [터미널(명령 프롬프트) 사용법](#터미널명령-프롬프트-사용법)
4. [코드 편집기 선택](#코드-편집기-선택)
5. [Git 기본 사용법](#git-기본-사용법)
6. [pip과 패키지 관리](#pip과-패키지-관리)
7. [가상환경이란?](#가상환경이란)
8. [Python 기초 빠른 복습](#python-기초-빠른-복습)

---

## 필요한 기본 지식

이 프로젝트를 따라하려면 다음 정도의 기본 지식이 필요합니다:

| 주제 | 필요 수준 | 내용 |
|------|----------|------|
| **Python** | 기초 | 변수, 함수, 클래스, 딕셔너리 |
| **터미널** | 기초 | 명령어 입력, 디렉토리 이동 |
| **Git** | 기초 | clone, commit 정도 |
| **웹 개념** | 없어도 됨 | [입문 가이드](../00_introduction.md)에서 설명 |

> Python 문법이 아직 익숙하지 않다면, 이 문서 아래쪽의 [Python 기초 빠른 복습](#python-기초-빠른-복습)을 먼저 읽어보세요.

---

## Python 설치하기

### 현재 Python이 설치되어 있는지 확인

터미널(또는 명령 프롬프트)을 열고 입력합니다:

```bash
python --version
```

또는:

```bash
python3 --version
```

`Python 3.10.x` 이상이 나오면 이미 설치되어 있습니다.

### Windows에서 설치

1. https://www.python.org/downloads/ 접속
2. "Download Python 3.12.x" 버튼 클릭
3. **중요: 설치 화면에서 "Add Python to PATH" 반드시 체크**
4. "Install Now" 클릭

```
┌──────────────────────────────────────────┐
│  Install Python 3.12.x                   │
│                                          │
│  ☑ Add Python 3.12 to PATH  ← 꼭 체크!  │
│                                          │
│  [Install Now]                           │
└──────────────────────────────────────────┘
```

> "Add to PATH"를 체크하지 않으면 터미널에서 `python` 명령어가 작동하지 않습니다.

### macOS에서 설치

```bash
# Homebrew가 설치되어 있다면:
brew install python@3.12

# Homebrew가 없다면 먼저 설치:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

또는 https://www.python.org/downloads/ 에서 직접 다운로드

### Linux (Ubuntu/Debian)에서 설치

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 설치 확인

```bash
python --version    # Python 3.12.x
pip --version       # pip 24.x.x
```

---

## 터미널(명령 프롬프트) 사용법

터미널은 **텍스트로 컴퓨터에 명령을 내리는 도구**입니다.
FastAPI 서버를 실행하거나 패키지를 설치할 때 사용합니다.

### 터미널 열기

| OS | 방법 |
|----|------|
| **Windows** | `Win + R` → `cmd` 입력 또는 "Windows Terminal" 검색 |
| **macOS** | `Cmd + Space` → "터미널" 검색 |
| **Linux** | `Ctrl + Alt + T` |

### 꼭 알아야 할 기본 명령어

```bash
# 현재 위치 확인
pwd                    # macOS/Linux
cd                     # Windows (아무것도 안 쓰면 현재 위치 출력)

# 폴더 내용 보기
ls                     # macOS/Linux
dir                    # Windows

# 폴더 이동
cd Documents           # Documents 폴더로 이동
cd ..                  # 상위 폴더로 이동
cd ~/projects          # 홈 디렉토리의 projects 폴더로 이동

# 폴더 생성
mkdir my-project       # my-project 폴더 생성

# 파일 내용 보기
cat filename.txt       # macOS/Linux
type filename.txt      # Windows

# 화면 지우기
clear                  # macOS/Linux
cls                    # Windows
```

### 터미널 사용 예시: 프로젝트 폴더로 이동

```bash
# 1. 홈 디렉토리로 이동
cd ~

# 2. projects 폴더 만들기 (없으면)
mkdir projects

# 3. projects 폴더로 이동
cd projects

# 4. 현재 위치 확인
pwd
# 출력: /home/사용자이름/projects
```

### 팁: 탭(Tab) 자동완성

파일이나 폴더 이름을 입력할 때 **Tab 키**를 누르면 자동완성됩니다:

```bash
cd Docu[Tab키]    →    cd Documents/
```

---

## 코드 편집기 선택

코드를 읽고 편집하기 위한 도구가 필요합니다.

### 추천: Visual Studio Code (VS Code)

**무료**이고, 가장 많이 사용되는 편집기입니다.

1. https://code.visualstudio.com/ 에서 다운로드
2. 설치 후 다음 확장 프로그램 설치:

| 확장 프로그램 | 설명 |
|-------------|------|
| **Python** (Microsoft) | Python 개발 필수 |
| **Pylance** | Python 코드 자동완성 |

### VS Code에서 터미널 사용

VS Code 안에서 터미널을 열 수 있습니다:
- 단축키: `` Ctrl + ` `` (백틱, 키보드 1 왼쪽)
- 또는 메뉴: `View` → `Terminal`

이렇게 하면 코드 편집과 터미널 작업을 한 화면에서 할 수 있습니다.

### VS Code에서 프로젝트 열기

```bash
# 터미널에서 프로젝트 폴더로 이동한 후:
code .    # 현재 폴더를 VS Code로 열기
```

또는 VS Code에서 `File` → `Open Folder` → 프로젝트 폴더 선택

---

## Git 기본 사용법

Git은 코드의 **버전을 관리하는 도구**입니다.
이 프로젝트의 소스 코드를 받으려면 Git이 필요합니다.

### Git 설치 확인

```bash
git --version
# git version 2.x.x 가 나오면 설치되어 있음
```

### Git 설치

- **Windows**: https://git-scm.com/download/win
- **macOS**: `brew install git` 또는 Xcode 설치 시 자동 포함
- **Linux**: `sudo apt install git`

### 이 프로젝트에서 사용할 Git 명령어

```bash
# 프로젝트 코드 받기 (처음 한 번만)
git clone <저장소-URL>
cd FastAPI_Tutorial

# 변경 사항 확인
git status

# 변경 사항 저장
git add .                         # 모든 변경 파일 준비
git commit -m "변경 내용 설명"      # 변경 기록 남기기
```

---

## pip과 패키지 관리

### pip이란?

pip은 Python의 **패키지 관리자**입니다.
스마트폰의 앱스토어처럼, 다른 개발자가 만든 라이브러리를 설치할 수 있습니다.

```bash
# 패키지 설치
pip install fastapi        # fastapi 패키지 설치

# 특정 버전 설치
pip install fastapi==0.109.0

# 여러 패키지 한꺼번에 설치 (requirements.txt 파일 사용)
pip install -r requirements.txt

# 설치된 패키지 목록 보기
pip list

# 패키지 삭제
pip uninstall fastapi
```

### requirements.txt란?

프로젝트에 필요한 패키지 목록을 적어놓은 파일입니다.

```txt
# requirements.txt 예시
fastapi==0.109.0          # 웹 프레임워크
uvicorn[standard]==0.27.0 # 서버 실행 도구
sqlalchemy==2.0.25        # 데이터베이스 ORM
```

`pip install -r requirements.txt` 명령어 하나로 필요한 패키지를 모두 설치할 수 있습니다.

---

## 가상환경이란?

### 문제 상황

```
프로젝트 A: fastapi 0.100.0 필요
프로젝트 B: fastapi 0.109.0 필요

같은 컴퓨터에서 두 프로젝트를 어떻게 관리하지? 🤔
```

### 해결: 가상환경

**가상환경은 프로젝트마다 독립적인 Python 패키지 공간을 만드는 것**입니다.

```
내 컴퓨터
├── 프로젝트A/ (가상환경 A)
│   └── fastapi 0.100.0    ← A만의 패키지
│
└── 프로젝트B/ (가상환경 B)
    └── fastapi 0.109.0    ← B만의 패키지
```

### 가상환경 사용법

```bash
# 1. 프로젝트 폴더로 이동
cd FastAPI_Tutorial

# 2. 가상환경 만들기 (한 번만)
python -m venv venv
# "venv"라는 이름의 가상환경 폴더가 생성됨

# 3. 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 활성화되면 터미널에 (venv) 표시가 나타남
(venv) $ pip install fastapi    # 이 가상환경에만 설치됨

# 5. 가상환경 비활성화 (작업 끝났을 때)
deactivate
```

### 가상환경이 활성화되었는지 확인하는 방법

터미널 맨 앞에 `(venv)`가 보이면 활성화된 상태입니다:

```bash
# 활성화 전:
$ python --version

# 활성화 후:
(venv) $ python --version    ← (venv) 표시가 보임
```

> **주의:** 항상 가상환경을 활성화한 상태에서 작업하세요!
> 그렇지 않으면 패키지가 시스템 전체에 설치되어 다른 프로젝트에 영향을 줄 수 있습니다.

---

## Python 기초 빠른 복습

이 프로젝트의 코드를 이해하는 데 필요한 Python 문법을 간단히 복습합니다.

### 1. 변수와 타입

```python
# 문자열
name = "홍길동"
email = "hong@example.com"

# 숫자
age = 25
price = 9900.5

# 불리언 (참/거짓)
is_active = True
is_admin = False

# None (값 없음)
nickname = None

# 리스트 (목록)
fruits = ["사과", "바나나", "포도"]
fruits[0]  # "사과"

# 딕셔너리 (키-값 쌍) ← JSON과 비슷!
user = {
    "name": "홍길동",
    "age": 25,
    "is_active": True
}
user["name"]  # "홍길동"
```

### 2. 타입 힌트 (FastAPI에서 많이 사용)

```python
# 타입 힌트 = 변수나 함수에 "이건 이런 타입이에요"라고 표시하는 것
# 실행에는 영향 없지만, FastAPI가 이를 활용함

name: str = "홍길동"          # 문자열
age: int = 25                 # 정수
price: float = 9900.5         # 소수
is_active: bool = True        # 불리언

# 함수의 타입 힌트
def greet(name: str) -> str:     # str을 받아서 str을 반환
    return f"안녕하세요, {name}!"

# Optional = 값이 있을 수도 없을 수도 있음
from typing import Optional
nickname: Optional[str] = None   # 문자열 또는 None
```

**왜 중요한가요?**
FastAPI는 타입 힌트를 보고:
- 데이터를 자동으로 검증함 (문자열이 와야 하는데 숫자가 오면 에러)
- API 문서를 자동으로 생성함

### 3. 함수와 데코레이터

```python
# 기본 함수
def add(a: int, b: int) -> int:
    return a + b

result = add(3, 5)  # 8

# 기본값이 있는 매개변수
def greet(name: str, greeting: str = "안녕하세요"):
    return f"{greeting}, {name}!"

greet("홍길동")                    # "안녕하세요, 홍길동!"
greet("홍길동", greeting="반갑습니다")  # "반갑습니다, 홍길동!"

# 데코레이터 = 함수에 추가 기능을 붙이는 것
# FastAPI에서 @ 기호로 많이 사용됩니다
@app.get("/hello")         # ← 데코레이터: 이 함수를 GET /hello URL에 연결
def say_hello():
    return {"message": "Hello!"}
```

### 4. 클래스

```python
# 클래스 = 데이터와 기능을 묶어놓은 것
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def greet(self) -> str:
        return f"안녕하세요, {self.name}입니다."

# 사용
user = User("홍길동", "hong@example.com")
print(user.name)     # "홍길동"
print(user.greet())  # "안녕하세요, 홍길동입니다."

# 상속 = 기존 클래스를 확장하는 것
class AdminUser(User):        # User를 상속받음
    def __init__(self, name: str, email: str):
        super().__init__(name, email)  # 부모 클래스 초기화
        self.role = "admin"

admin = AdminUser("관리자", "admin@example.com")
print(admin.role)    # "admin"
print(admin.greet()) # "안녕하세요, 관리자입니다." (부모 메서드 사용 가능)
```

**이 프로젝트에서의 활용:**
```python
# Pydantic 모델 (데이터 검증용)
from pydantic import BaseModel

class UserCreate(BaseModel):       # BaseModel 상속
    email: str
    username: str
    password: str

# SQLAlchemy 모델 (DB 테이블 정의)
from app.database import Base

class User(Base):                   # Base 상속
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
```

### 5. 딕셔너리 언패킹 (`**`)

```python
# ** = 딕셔너리를 풀어서 전달
data = {"name": "홍길동", "age": 25}

# 이것과
User(name="홍길동", age=25)

# 이것은 같습니다
User(**data)

# 프로젝트에서 자주 보이는 패턴:
post = Post(**post_data.model_dump())
# post_data의 모든 필드를 Post 모델에 전달
```

### 6. async/await (비동기)

```python
# async = "이 함수는 비동기입니다"
# await = "이 작업이 끝날 때까지 기다립니다"

# 동기 함수 (일반 함수)
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# 비동기 함수
async def get_user(user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

> **참고:** FastAPI는 동기(`def`)와 비동기(`async def`) 함수 모두 지원합니다.
> 이 프로젝트에서는 주로 동기 함수를 사용합니다.

### 7. with 문과 yield

```python
# with문 = 시작과 끝에 자동으로 작업을 수행
with open("file.txt") as f:    # 파일 열기
    content = f.read()
# with 블록이 끝나면 파일이 자동으로 닫힘

# yield = 값을 반환하되, 함수가 끝나지 않음
def get_db():
    db = SessionLocal()     # DB 연결 생성
    try:
        yield db            # db를 반환하고 잠시 멈춤
    finally:
        db.close()          # 사용이 끝나면 연결 닫기

# FastAPI가 이런 패턴을 많이 사용합니다 (의존성 주입)
```

---

## 준비 완료 체크리스트

다음 항목을 모두 확인했다면, 프로젝트를 시작할 준비가 된 것입니다:

- [ ] Python 3.10 이상이 설치되어 있다
- [ ] 터미널에서 `python --version`이 정상 작동한다
- [ ] 터미널에서 `pip --version`이 정상 작동한다
- [ ] Git이 설치되어 있다 (`git --version`)
- [ ] 코드 편집기가 준비되어 있다 (VS Code 등)
- [ ] 가상환경의 개념을 이해했다

---

## 다음 단계

준비가 되었다면 [설치 가이드](../01_installation.md)로 이동하여 프로젝트를 실제로 설치하고 실행해보세요!

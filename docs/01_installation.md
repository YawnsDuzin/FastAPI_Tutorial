# 설치 가이드

이 문서에서는 FastAPI 보일러플레이트 프로젝트를 설치하고 실행하는 방법을 설명합니다.

> 웹 개발이 처음이라면 먼저 [입문 가이드](00_introduction.md)와 [개발 환경 준비](tutorial/00_before_you_start.md)를 읽어보세요.

## 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [프로젝트 설치](#프로젝트-설치)
3. [데이터베이스 설정](#데이터베이스-설정)
4. [서버 실행](#서버-실행)
5. [잘 되는지 확인하기](#잘-되는지-확인하기)
6. [Docker로 실행](#docker로-실행)
7. [자주 발생하는 문제 해결](#자주-발생하는-문제-해결)

---

## 시스템 요구사항

### 필수 사항

- **Python**: 3.10 이상
- **pip**: 최신 버전 권장
- **데이터베이스**: PostgreSQL, MySQL, MariaDB, 또는 SQLite

### 선택 사항

- **Docker**: 컨테이너 기반 실행 시
- **Git**: 버전 관리

> **초보자 팁:** 처음이라면 SQLite를 사용하세요. 별도 설치 없이 바로 사용할 수 있습니다.

---

## 프로젝트 설치

### 1. 저장소 클론

```bash
git clone <repository-url>
cd FastAPI_Tutorial
```

> **"클론(clone)"이란?** 원격 저장소(GitHub 등)에 있는 코드를 내 컴퓨터에 복사하는 것입니다.

### 2. 가상환경 생성

가상환경을 사용하여 의존성을 격리합니다.

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

활성화에 성공하면 터미널 맨 앞에 `(venv)`가 표시됩니다:

```bash
(venv) $           ← 이렇게 보이면 성공!
```

> **가상환경을 왜 써야 하나요?**
> 프로젝트마다 필요한 패키지 버전이 다를 수 있습니다.
> 가상환경을 사용하면 프로젝트별로 패키지를 분리 관리할 수 있어서, 다른 프로젝트에 영향을 주지 않습니다.
> 자세한 설명은 [개발 환경 준비 - 가상환경이란?](tutorial/00_before_you_start.md#가상환경이란)을 참고하세요.

### 3. 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **이 명령어가 하는 일:**
> 1. `pip install --upgrade pip`: pip 자체를 최신 버전으로 업데이트
> 2. `pip install -r requirements.txt`: 프로젝트에 필요한 패키지를 모두 설치
>
> `requirements.txt` 파일에 FastAPI, SQLAlchemy, JWT 인증 라이브러리 등 필요한 모든 패키지가 적혀 있습니다.

**설치가 정상적으로 되었는지 확인:**

```bash
pip list | grep fastapi
# fastapi 0.109.0 이 보이면 성공
```

### 4. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일 편집 (자신의 환경에 맞게 수정)
nano .env  # 또는 원하는 편집기 사용
```

> **환경 변수(.env)란?**
> 비밀번호, DB 접속 정보 등 **코드에 직접 쓰면 안 되는 민감한 정보**를 별도 파일에 저장하는 것입니다.
> `.env` 파일은 Git에 올라가지 않도록 `.gitignore`에 등록되어 있습니다.
>
> **비유:** 집 열쇠를 문 앞 화분 밑에 놓는 대신, 안전한 곳에 보관하는 것과 같습니다.

**초보자를 위한 최소 .env 설정 (SQLite 사용):**

```env
# .env 파일 내용 (SQLite를 사용하면 이것만 있으면 됩니다)
DB_TYPE=sqlite
SQLITE_FILE=./data/app.db
SECRET_KEY=my-dev-secret-key-change-this-in-production
JWT_SECRET_KEY=my-jwt-secret-key-change-this-in-production
DEBUG=true
```

---

## 데이터베이스 설정

### 어떤 데이터베이스를 선택해야 하나요?

| 데이터베이스 | 추천 대상 | 장점 | 단점 |
|------------|----------|------|------|
| **SQLite** | 입문자, 개발용 | 설치 불필요, 간편 | 동시 접속에 약함 |
| **PostgreSQL** | 프로덕션 | 안정적, 기능 풍부 | 별도 설치 필요 |
| **MySQL/MariaDB** | 프로덕션 | 빠름, 대중적 | 별도 설치 필요 |

> **처음이라면 SQLite를 추천합니다.** 별도 설치 없이 바로 사용할 수 있고, 나중에 PostgreSQL 등으로 변경하기도 쉽습니다.

### SQLite (개발용) - 가장 간단한 선택

SQLite는 별도 설치 없이 사용할 수 있습니다. 파일 하나에 데이터가 저장됩니다.

#### .env 설정

```env
DB_TYPE=sqlite
SQLITE_FILE=./data/app.db
```

`data` 디렉토리는 서버 시작 시 자동으로 생성됩니다.

> **SQLite란?** 별도 서버 없이 파일 하나로 동작하는 경량 데이터베이스입니다.
> 개발 및 학습 용도로 적합합니다.

### PostgreSQL (기본 권장)

실제 서비스를 운영한다면 PostgreSQL을 권장합니다.

#### 설치

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# https://www.postgresql.org/download/windows/ 에서 다운로드
```

#### 데이터베이스 생성

```bash
# PostgreSQL에 접속
sudo -u postgres psql

# 데이터베이스 및 사용자 생성
CREATE USER fastapi_user WITH PASSWORD 'your_password';
CREATE DATABASE fastapi_db OWNER fastapi_user;
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
\q
```

> **이 명령어들이 하는 일:**
> 1. `CREATE USER`: DB에 접속할 사용자 계정 생성
> 2. `CREATE DATABASE`: 데이터를 저장할 데이터베이스 생성
> 3. `GRANT ALL PRIVILEGES`: 해당 사용자에게 DB 사용 권한 부여
> 4. `\q`: PostgreSQL 접속 종료

#### .env 설정

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=fastapi_user
DB_PASSWORD=your_password
DB_NAME=fastapi_db
```

> **각 항목의 의미:**
> - `DB_TYPE`: 사용할 DB 종류
> - `DB_HOST`: DB 서버 주소 (`localhost` = 내 컴퓨터)
> - `DB_PORT`: DB 서버 포트번호 (PostgreSQL 기본: 5432)
> - `DB_USER` / `DB_PASSWORD`: DB 접속 계정
> - `DB_NAME`: 사용할 데이터베이스 이름

### MySQL/MariaDB

#### 설치

```bash
# Ubuntu/Debian
sudo apt install mysql-server
# 또는
sudo apt install mariadb-server

# macOS (Homebrew)
brew install mysql
# 또는
brew install mariadb
```

#### 데이터베이스 생성

```bash
# MySQL에 접속
mysql -u root -p

# 데이터베이스 및 사용자 생성
CREATE DATABASE fastapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON fastapi_db.* TO 'fastapi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

> **`utf8mb4`란?** 한글, 이모지 등을 포함한 모든 유니코드 문자를 저장할 수 있는 문자 인코딩입니다.
> 한국어를 사용한다면 반드시 `utf8mb4`로 설정해야 합니다.

#### .env 설정

```env
DB_TYPE=mysql  # 또는 mariadb
DB_HOST=localhost
DB_PORT=3306
DB_USER=fastapi_user
DB_PASSWORD=your_password
DB_NAME=fastapi_db
```

---

## 서버 실행

### 개발 서버

```bash
# 기본 실행 (핫 리로드 활성화)
uvicorn app.main:app --reload
```

> **이 명령어 분석:**
> - `uvicorn`: FastAPI 서버를 실행하는 도구
> - `app.main:app`: `app` 폴더의 `main.py` 파일에 있는 `app` 객체를 실행
> - `--reload`: 코드를 수정하면 서버가 자동으로 재시작 (개발할 때 편리)

**성공하면 이런 메시지가 나타납니다:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**서버 종료:** `Ctrl + C`를 누르면 됩니다.

### 자주 사용하는 실행 옵션

```bash
# 특정 포트 지정
uvicorn app.main:app --reload --port 8080

# 모든 인터페이스에서 접속 허용 (다른 컴퓨터에서도 접속 가능)
uvicorn app.main:app --reload --host 0.0.0.0

# 워커 수 지정 (프로덕션)
uvicorn app.main:app --workers 4
```

> **포트(Port)란?** 컴퓨터의 "문 번호"라고 생각하면 됩니다.
> 웹 서버는 보통 8000번 또는 8080번 포트를 사용합니다.
> `--port 8080`은 "8080번 문으로 들어오세요"라는 뜻입니다.

### 프로덕션 서버

프로덕션 환경에서는 Gunicorn과 함께 사용하는 것을 권장합니다.

```bash
# Gunicorn 설치
pip install gunicorn

# 실행
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

> **프로덕션이란?** 실제 사용자에게 서비스를 제공하는 운영 환경입니다.
> 개발 환경과 달리 `--reload` 없이, 여러 워커(worker)를 사용하여 안정적으로 실행합니다.

---

## 잘 되는지 확인하기

서버가 실행된 상태에서 다음 URL에 접속해보세요:

### 1. API 루트 확인

브라우저에서 http://localhost:8000 접속

### 2. 헬스 체크

브라우저에서 http://localhost:8000/health 접속

```json
{
    "status": "healthy",
    "database": "sqlite"
}
```

이런 응답이 보이면 서버가 정상 작동하는 것입니다!

### 3. Swagger UI (API 테스트 도구)

**http://localhost:8000/docs** 에 접속하면 API를 직접 테스트할 수 있는 화면이 나타납니다.

> **Swagger UI란?** FastAPI가 자동으로 생성하는 API 테스트 페이지입니다.
> 코드를 작성하면 자동으로 문서가 만들어지며, 이 화면에서 직접 API를 호출해볼 수 있습니다.
> 자세한 사용법은 [사용 가이드](03_usage.md)에서 설명합니다.

### 4. ReDoc (API 문서)

**http://localhost:8000/redoc** 에 접속하면 깔끔한 형태의 API 문서를 볼 수 있습니다.

### 요약

| URL | 설명 |
|-----|------|
| http://localhost:8000 | API 루트 |
| http://localhost:8000/health | 서버 상태 확인 |
| http://localhost:8000/docs | Swagger UI (API 테스트) |
| http://localhost:8000/redoc | ReDoc (API 문서) |

---

## Docker로 실행

> **Docker란?** 애플리케이션을 독립적인 컨테이너에서 실행하는 기술입니다.
> "내 컴퓨터에서는 되는데 다른 컴퓨터에서는 안 돼요" 문제를 해결합니다.
> Docker를 사용하면 동일한 환경을 어디서든 재현할 수 있습니다.
>
> **초보자 팁:** Docker가 처음이라면 이 섹션은 건너뛰고, 위의 방법으로 먼저 실행해보세요.

### Dockerfile 생성

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml 생성

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_TYPE=postgresql
      - DB_HOST=db
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_NAME=fastapi_db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Docker 실행

```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 자주 발생하는 문제 해결

### "python 명령어를 찾을 수 없습니다"

```bash
# python 대신 python3 사용
python3 --version
python3 -m venv venv

# 또는 Windows에서 Python 설치 시 "Add to PATH" 체크 확인
```

### "pip 명령어를 찾을 수 없습니다"

```bash
# pip 대신 pip3 사용
pip3 install -r requirements.txt

# 또는 python -m pip 사용
python -m pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'fastapi'"

가상환경이 활성화되지 않은 상태에서 실행하면 이 에러가 발생합니다.

```bash
# 가상환경 활성화 후 다시 실행
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate         # Windows

# 패키지가 설치되어 있는지 확인
pip list | grep fastapi
```

### "Address already in use" (포트가 이미 사용 중)

다른 프로그램이 8000번 포트를 사용하고 있을 때 발생합니다.

```bash
# 다른 포트 사용
uvicorn app.main:app --reload --port 8001

# 또는 8000번 포트를 사용하는 프로세스 종료
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID번호> /F
```

### "데이터베이스 연결 실패"

```bash
# .env 파일 설정 확인
cat .env

# SQLite 사용 시 data 디렉토리가 없으면 생성
mkdir -p data

# PostgreSQL 사용 시 서비스 실행 확인
# macOS:
brew services start postgresql
# Linux:
sudo systemctl start postgresql
```

### "Permission denied" (권한 오류)

```bash
# Linux/macOS에서 실행 권한 필요할 때
chmod +x venv/bin/activate

# 관리자 권한으로 실행 (pip 설치 실패 시)
pip install --user -r requirements.txt
```

---

## 다음 단계

설치가 완료되면 다음 문서를 참조하세요:

- [환경 설정](02_configuration.md): 상세 설정 옵션
- [사용 가이드](03_usage.md): API 사용 방법
- [API 레퍼런스](04_api_reference.md): 전체 API 문서

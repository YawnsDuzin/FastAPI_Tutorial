"""
Logging Configuration
======================

애플리케이션 로깅을 설정하고 관리하는 모듈입니다.

Features:
- 콘솔 및 파일 로깅
- 로그 로테이션 (RotatingFileHandler)
- JSON 포맷 지원
- 환경별 로그 레벨 설정
"""

import logging
import sys
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.config import settings


class JsonFormatter(logging.Formatter):
    """
    JSON 형식의 로그 포맷터

    구조화된 로그를 JSON 형태로 출력합니다.
    로그 수집 시스템과 연동 시 유용합니다.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 예외 정보가 있으면 추가
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 추가 필드가 있으면 포함
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: Optional[str] = None,
    log_file_enabled: Optional[bool] = None,
    log_file_path: Optional[str] = None,
) -> logging.Logger:
    """
    애플리케이션 로깅을 설정합니다.

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file_enabled: 파일 로깅 활성화 여부
        log_file_path: 로그 파일 경로

    Returns:
        logging.Logger: 설정된 루트 로거
    """
    # 설정값 결정 (파라미터 > 환경설정)
    level = log_level or settings.log_level
    file_enabled = log_file_enabled if log_file_enabled is not None else settings.log_file_enabled
    file_path = log_file_path or settings.log_file_path

    # 로그 레벨 변환
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # 루트 로거 가져오기
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # 포맷터 생성
    if settings.log_json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt=settings.log_format,
            datefmt=settings.log_date_format
        )

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 설정
    if file_enabled:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=settings.log_file_max_bytes,
            backupCount=settings.log_file_backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거를 반환합니다.

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        logging.Logger: 해당 이름의 로거

    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("메시지")
    """
    return logging.getLogger(name)


# 애플리케이션 시작 시 자동으로 로깅 설정
_initialized = False


def init_logging() -> logging.Logger:
    """
    로깅 시스템을 초기화합니다.

    이 함수는 애플리케이션 시작 시 한 번만 호출됩니다.

    Returns:
        logging.Logger: 설정된 루트 로거
    """
    global _initialized
    if not _initialized:
        setup_logging()
        _initialized = True
        logger = get_logger(__name__)
        logger.debug("로깅 시스템 초기화 완료")
    return logging.getLogger()

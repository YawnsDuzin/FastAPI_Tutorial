"""
Logging Middleware
==================

HTTP 요청/응답을 로깅하는 미들웨어입니다.

Features:
- 요청 메서드, 경로, 클라이언트 IP 로깅
- 응답 상태 코드 및 처리 시간 로깅
- 에러 발생 시 상세 로깅
- 헬스 체크 등 특정 경로 제외 가능
"""

import time
import uuid
from typing import Callable, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청/응답 로깅 미들웨어

    모든 HTTP 요청과 응답을 로깅합니다.
    요청 처리 시간도 함께 기록합니다.
    """

    def __init__(
        self,
        app,
        exclude_paths: List[str] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        """
        미들웨어 초기화

        Args:
            app: FastAPI/Starlette 애플리케이션
            exclude_paths: 로깅에서 제외할 경로 목록
            log_request_body: 요청 본문 로깅 여부 (주의: 민감 정보)
            log_response_body: 응답 본문 로깅 여부 (주의: 성능 영향)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청을 처리하고 로깅합니다.

        Args:
            request: HTTP 요청 객체
            call_next: 다음 미들웨어/핸들러 호출 함수

        Returns:
            Response: HTTP 응답 객체
        """
        # 제외 경로 체크
        if self._should_skip_logging(request.url.path):
            return await call_next(request)

        # 요청 ID 생성 (추적용)
        request_id = str(uuid.uuid4())[:8]

        # 요청 시작 시간
        start_time = time.time()

        # 클라이언트 정보
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        query_string = str(request.query_params) if request.query_params else ""

        # 요청 로깅
        logger.info(
            f"[{request_id}] --> {method} {path}"
            f"{('?' + query_string) if query_string else ''} "
            f"| Client: {client_ip}"
        )

        # 요청 처리
        try:
            response = await call_next(request)

            # 처리 시간 계산
            process_time = (time.time() - start_time) * 1000  # ms

            # 응답 로깅
            status_code = response.status_code
            log_level = self._get_log_level_for_status(status_code)

            log_message = (
                f"[{request_id}] <-- {method} {path} "
                f"| Status: {status_code} "
                f"| Time: {process_time:.2f}ms"
            )

            if log_level == "warning":
                logger.warning(log_message)
            elif log_level == "error":
                logger.error(log_message)
            else:
                logger.info(log_message)

            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # 에러 처리 시간 계산
            process_time = (time.time() - start_time) * 1000

            # 에러 로깅
            logger.error(
                f"[{request_id}] <-- {method} {path} "
                f"| Error: {type(e).__name__}: {str(e)} "
                f"| Time: {process_time:.2f}ms",
                exc_info=True
            )
            raise

    def _should_skip_logging(self, path: str) -> bool:
        """로깅을 건너뛸지 결정합니다."""
        return any(path.startswith(exclude) for exclude in self.exclude_paths)

    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP를 추출합니다."""
        # X-Forwarded-For 헤더 확인 (프록시/로드밸런서 뒤에 있는 경우)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 직접 연결된 클라이언트 IP
        if request.client:
            return request.client.host

        return "unknown"

    def _get_log_level_for_status(self, status_code: int) -> str:
        """상태 코드에 따른 로그 레벨을 반환합니다."""
        if status_code >= 500:
            return "error"
        elif status_code >= 400:
            return "warning"
        return "info"

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        
        logger.info(
            f"endpoint: {request.url.path} | Method: {request.method} | "
            f"Status: {response.status_code} | Duration: {duration:.4f}s"
        )
        return response

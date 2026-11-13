import logging
import time
import uuid

from .logs import request_id_var

logger = logging.getLogger("core.request")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            logger.info("request", extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                "user_id": getattr(getattr(request, "user", None), "pk", None),
            })
            return response
        finally:
            request_id_var.reset(token)

import datetime
import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from backend.core.api.request_id_var import (
    get_request_id,
    reset_request_id,
    set_request_id,
)

logger = logging.getLogger(__name__)


class RequestContextLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if "X-Request-ID" in request.headers:
            request_id_value = request.headers.get("X-Request-ID")
        else:
            request_id_value = str(uuid4())
        request_id = set_request_id(request_id_value)

        logger.info("%s %s?%s", request.method, request.url.path, request.url.query)
        start_time = time.time()
        response = await call_next(request)
        response.headers["X-Request-ID"] = get_request_id()
        str_duration = str(datetime.timedelta(seconds=time.time() - start_time))
        logger.info(f"request executed in {str_duration}")

        reset_request_id(request_id)

        return response

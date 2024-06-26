import logging
from contextvars import ContextVar

REQUEST_ID_CTX_KEY = "request_id"

_request_id_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def set_request_id(request_id):
    return _request_id_ctx_var.set(request_id)


def get_request_id() -> str:
    return _request_id_ctx_var.get()


def reset_request_id(request_id):
    _request_id_ctx_var.reset(request_id)


class AppFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True

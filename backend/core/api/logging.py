import logging
import sys

from backend.core.api.request_id_var import AppFilter


def setup_logging(level: int) -> None:
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = False
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    logger = logging.getLogger()
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    syslog = logging.StreamHandler(sys.stdout)
    syslog.addFilter(AppFilter())

    formatter = logging.Formatter(
        "[%(asctime)s|%(process)d|%(request_id).8s..] %(levelname)8s: %(message)s",
    )

    syslog.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(syslog)

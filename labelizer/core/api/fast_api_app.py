import logging
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI
from fastapi.exceptions import ValidationException
from starlette.exceptions import HTTPException

from labelizer import APP_VERSION
from labelizer.core.api.logging import setup_logging
from labelizer.core.api.middlewares import RequestContextLogMiddleware
from labelizer.routes import router as label_router

description = """
API used to generate and manage triplets of images for labeling.
"""

ROOT_PATH = "/api/labelizer/v1"

def setup_app() -> FastAPI:
    """
    Initialize fastapi app.
    """
    _app = FastAPI(
        title="Labelizer API",
        description=description,
        version=APP_VERSION,
        openapi_url=ROOT_PATH + "/openapi.json",
        docs_url=ROOT_PATH + "/docs",
        redoc_url=None,
        # responses={
        #     "default": {"message": "Response on failure", "model": ErrorReponse}
        # },
    )

    _app.add_middleware(RequestContextLogMiddleware)

    setup_logging(logging.INFO)

    routers = [
        label_router
    ]
    for router in routers:
        _app.include_router(router, prefix=ROOT_PATH)

    # exception_handlers = {
    #     (http_exception_handler, HTTPException),
    #     (validation_exception_handler, ValidationException),
    #     (
    #         proact_logistics_auth_exception_handler,
    #         ProACTLogisticsAuthentificationException,
    #     ),
    #     (
    #         proact_logistics_validation_exception_handler,
    #         ProACTLogisticsValidationException,
    #     ),
    #     (
    #         proact_logistics_validation_exception_handler,
    #         ProACTLogisticsInternalException,
    #     ),
    # }
    # for handler, exception_class in exception_handlers:
    #     _app.add_exception_handler(exception_class, handler)

    return _app


app = setup_app()


@app.get("/")
def root():
    return {"message": f"documentation is located at {ROOT_PATH}/docs"}

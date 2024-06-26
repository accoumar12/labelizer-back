import logging

from fastapi import FastAPI

from src import APP_VERSION
from src.config.routes import router as config_router
from src.core.api.logging import setup_logging
from src.core.api.middlewares import RequestContextLogMiddleware
from src.core.database.core import Base, engine
from src.core.database.manage import init_database
from src.images_utils.routes import router as images_router
from src.similarity.routes import router as similarity_router
from src.triplets.routes import router as triplets_router
from src.upload.routes import router as upload_router

description = """
Labelizer API.
"""

ROOT_PATH = "/api/labelizer/v1"


def setup_app() -> FastAPI:
    """Initialize fastapi app."""
    setup_logging(logging.DEBUG)

    init_database(engine)

    Base.metadata.create_all(bind=engine)

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

    routers = [
        config_router,
        upload_router,
        triplets_router,
        similarity_router,
        images_router,
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
def root() -> dict:
    return {"message": f"documentation is located at {ROOT_PATH}/docs"}

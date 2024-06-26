# Not optimal to give the config this way, would be better to have a common config module to the backend and the frontend
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.config.app_config import app_config

router = APIRouter(tags=["Config"])


@router.get(
    "/config",
    summary="Get some configuration variables of the app.",
)
def get_config() -> JSONResponse:
    return JSONResponse(
        content={
            "lock_timeout_in_seconds": app_config.lock_timeout_in_seconds,
        },
        status_code=status.HTTP_200_OK,
    )

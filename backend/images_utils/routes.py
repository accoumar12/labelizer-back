import logging

from fastapi import APIRouter, status
from starlette.responses import FileResponse

from backend.config.config import config
from backend.core.api.auth.core import UserSession

router = APIRouter(tags=["Images"])

logger = logging.getLogger()


@router.get(
    "/images/{image_id}",
    summary="Retrieve an image by its id. Does not need the extension. If you need the canonical image, provide 'canonical=true' as a query parameter.",
    status_code=status.HTTP_200_OK,
)
async def get_image(
    user: UserSession,
    image_id: str,
    canonical: bool = False,
) -> FileResponse:
    suffix = "_canonical" if canonical else ""
    logger.info("Image %s%s retrieved.", image_id, suffix)
    return FileResponse(f"{config.images_path}/{image_id}{suffix}.stp.png")

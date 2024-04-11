import os
from pathlib import Path

from fastapi import APIRouter, Depends, status
from starlette.responses import FileResponse

from labelizer.core.database.init_database import SessionLocal
from labelizer.schemas import LabelizerTripletResponse, SelectedItemType

router = APIRouter(tags=["Studies Management"])

# IMAGES_PATH has to be set as an environment variable
images_path = Path(os.environ['IMAGES_PATH'])

@router.get(
    "/images/{image_id}",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def get_image(image_id:str) -> FileResponse:
    return FileResponse(f'{images_path}/{image_id}')

@router.get(
    "/triplet",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def make_labelizer_triplet(
) -> LabelizerTripletResponse:

    result = LabelizerTripletResponse("0", "0", "0", "0")

    return result

@router.post(
    "/triplet",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def set_triplet_label(
    user_id:str,
    request_id:str,
    label:SelectedItemType,
) -> None:
    """
    TODO
    """
     

    
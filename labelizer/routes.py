from fastapi import APIRouter, status
from starlette.responses import FileResponse

from labelizer.core.database.database import get_db
from labelizer.model import LabelizerTripletResponse, SelectedItemType

router = APIRouter(tags=["Studies Management"])

@router.get(
    "/images",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def get_image(user_id:str, image_id:str):
    return FileResponse(f'/images/{image_id}')

@router.get(
    "/triplet",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def make_labelizer_triplet(
) -> LabelizerTripletResponse:
    with get_db() as session:
        # result = get_triplet(session)
        result = 0

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
):
    """
    TODO
    """
     

    
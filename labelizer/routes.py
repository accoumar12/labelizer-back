from fastapi import APIRouter, Depends, status
from starlette.responses import FileResponse

from labelizer.core.database.init_database import SessionLocal
from labelizer.model import LabelizerTripletResponse, SelectedItemType

router = APIRouter(tags=["Studies Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/images",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def get_image(user_id:str, image_id:str) -> FileResponse:
    return FileResponse(f'/images/{image_id}')

@router.get(
    "/triplet",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def make_labelizer_triplet(Session = Depends(get_db)
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
     

    
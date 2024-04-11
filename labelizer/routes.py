import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from labelizer import crud, schemas
from labelizer.core.database.init_database import SessionLocal
from labelizer.utils import SelectedItemType

router = APIRouter(tags=["Studies Management"])
t
# IMAGES_PATH has to be set as an environment variable
images_path = Path(os.environ['IMAGES_PATH'])

#TODO Add endpoint that downloads the database in csv format or excell, another one that appends the database with new triplets (zip as parameter, un dossier avec images et fichier triplet.csv), another one that deletes the database. All this for simplicity of use. Must : add a database parameter.

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
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
def make_triplet(
    db: Session = Depends(get_db),
) -> schemas.LabelizerTripletResponse:
    triplet = crud.get_first_unlabeled_triplet(db)
    if triplet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No unlabeled triplet found")
    triplet = schemas.LabelizerTripletResponse(id=triplet.id, reference_id=triplet.reference_id, left_id=triplet.left_id, right_id=triplet.right_id)
    return triplet

@router.post(
    "/triplet",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
def set_triplet_label(
    # user_id:str,
    triplet_id:str,
    label:SelectedItemType,
) -> None:
    ...     

    user_id = "email"
    
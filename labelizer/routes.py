import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from labelizer import crud, schemas
from labelizer.core.database.init_database import SessionLocal
from labelizer.utils import SelectedItemType

router = APIRouter(tags=["Triplet Management"])

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
    summary="Retrieve an image by its id.",
    status_code=status.HTTP_200_OK,
)
async def get_image(image_id:str) -> FileResponse:
    return FileResponse(f'{images_path}/{image_id}')


@router.get(
    "/triplet",
    summary="Get the first unlabeled triplet, in order to propose it to the user.",
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
    summary="Set the label of a triplet according to the user's choice.",
    status_code=status.HTTP_200_OK,
)
def set_triplet_label(
    #TODO add user_id:str,
    triplet_id:str,
    label:SelectedItemType,
    db: Session = Depends(get_db)
) -> JSONResponse:
    try:
        crud.set_triplet_label(db, triplet_id, label)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(content={"message": "Label set successfully"}, status_code=status.HTTP_200_OK)

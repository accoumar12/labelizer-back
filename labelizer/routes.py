import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from labelizer import crud, schemas
from labelizer.core.api.auth.core import AdminUserSession, UserSession
from labelizer.core.database.init_database import SessionLocal
from labelizer.utils import SelectedItemType

router = APIRouter(tags=["Triplet Management"])


#!!! ROOT_PATH has to be set as an environment variable, this is the path to the root of the project
root_path = Path(os.environ["ROOT_PATH"])

# Path to the images folder
images_path = os.path.join(root_path, "images")

# Path to the data folder, where the uploaded data is stored before being processed
uploaded_data_path = os.path.join(root_path, "data", "data")

# TODO: Add a parameter for the database used


# Dependency on the database
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
async def get_image(image_id: str) -> FileResponse:
    return FileResponse(f"{images_path}/{image_id}")


@router.get(
    "/triplet",
    summary="Get the triplet for the user of the app (it is actually the first unlabeled triplet of the database).",
    status_code=status.HTTP_200_OK,
)
def make_triplet(db: Session = Depends(get_db)) -> schemas.LabelizerTripletResponse:
    triplet = crud.get_first_unlabeled_triplet(db)
    if triplet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No unlabeled triplet found."
        )
    triplet = schemas.LabelizerTripletResponse(
        id=triplet.id,
        reference_id=triplet.reference_id,
        left_id=triplet.left_id,
        right_id=triplet.right_id,
    )
    return triplet


@router.post(
    "/triplet",
    summary="Set the label of a triplet according to the user's choice.",
    status_code=status.HTTP_200_OK,
)
def set_triplet_label(
    user: UserSession,
    triplet_id: str,
    label: SelectedItemType,
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        crud.set_triplet_label(db, triplet_id, label, user.uid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return JSONResponse(
        content={"message": "Label set successfully."}, status_code=status.HTTP_200_OK
    )


@router.get(
    "/download_db",
    summary="Download all the database in the csv format.",
    status_code=status.HTTP_200_OK,
)
def download_db(db: Session = Depends(get_db)) -> FileResponse:
    data = crud.get_all_data(db)
    df = pd.DataFrame(data)
    df.to_csv("database.csv")
    return FileResponse("database.csv")


@router.post(
    "/upload_data",
    summary="Upload new data, including images and triplets. The data has to be a zipped folder containing a csv file named triplets.csv and a folder named images containing the images.",
    status_code=status.HTTP_201_CREATED,
)
def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)) -> None:
    if file.filename.endswith(".zip"):
        # Extract the csv file
        with zipfile.ZipFile(file.file, "r") as zip_ref:
            zip_ref.extractall("data")

        # Add the triplets to the database
        df = pd.read_csv(f"{uploaded_data_path}/triplets.csv")
        crud.create_labelized_triplets(db, df)

        # Add the new images
        uploaded_images_path = os.path.join(uploaded_data_path, "images")
        for filename in os.listdir(uploaded_images_path):
            shutil.move(
                os.path.join(uploaded_images_path, filename),
                os.path.join(images_path, filename),
            )


@router.delete(
    "/delete_db",
    summary="Delete all the data inside the database.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_db(user: AdminUserSession, db: Session = Depends(get_db)) -> None:
    crud.delete_all_data(db)

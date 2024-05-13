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


#! ROOT_PATH has to be set as an environment variable, this is the path to the root of the project
root_path = Path(os.environ["ROOT_PATH"])

# Path to the images folder, where the images used by the backend are stored
images_path = root_path / "images"

# Path to the data folder, where the uploaded data is stored before being processed
uploaded_data_path = root_path / "data" / "data"


# Dependency on the database
def get_db() -> SessionLocal:
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
    return schemas.LabelizerTripletResponse(
        id=triplet.id,
        reference_id=triplet.reference_id,
        left_id=triplet.left_id,
        right_id=triplet.right_id,
    )


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    return JSONResponse(
        content={"message": "Label set successfully."},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/download_db",
    summary="Download all the database in the csv format. Needs to be authorized as an admin user.",
    status_code=status.HTTP_200_OK,
)
def download_db(user: AdminUserSession, db: Session = Depends(get_db)) -> FileResponse:
    data = crud.get_all_data(db)
    data = pd.DataFrame(data)
    data.to_csv("database.csv")
    return FileResponse("database.csv")


@router.post(
    "/upload_data",
    summary="Upload new data, including images and triplets. The data has to be a zipped folder containing a csv file named triplets.csv and a folder named images containing the images. Needs to be authorized as an admin user.",
    status_code=status.HTTP_201_CREATED,
)
async def upload_data(
    user: AdminUserSession, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> JSONResponse:
    if file.filename.endswith(".zip"):
        # Extract the csv file
        with zipfile.ZipFile(file.file, "r") as zip_ref:
            zip_ref.extractall("data")

        if not Path("data/data").exists():
            shutil.rmtree(uploaded_data_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The root folder in the zip file should be named 'data'.",
            )

        if not Path("data/data/images").exists():
            shutil.rmtree(uploaded_data_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The images folder should be named 'images'.",
            )

        if not Path("data/data/triplets.csv").exists():
            shutil.rmtree(uploaded_data_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The csv file should be named 'triplets.csv'.",
            )

        # Remove the desktop.ini file that is sometimes added by Windows
        if Path(f"{uploaded_data_path}/images/desktop.ini").exists():
            Path(f"{uploaded_data_path}/images/desktop.ini").unlink()

        # Add the triplets to the database
        triplets = pd.read_csv(f"{uploaded_data_path}/triplets.csv")

        # Check if each value in the triplets corresponds to an image that is loaded
        uploaded_images_path = uploaded_data_path / "images"
        uploaded_images = set(os.listdir(uploaded_images_path))
        triplet_values = set(triplets.to_numpy().flatten())

        missing_images = triplet_values - uploaded_images
        if missing_images:
            shutil.rmtree(uploaded_data_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing images for these triplet values: {missing_images}.",
            )

        # Check if there are extra images that do not have any value in the triplets
        extra_images = uploaded_images - triplet_values
        if extra_images:
            shutil.rmtree(uploaded_data_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extra images that do not have any value in the triplets: {extra_images}.",
            )

        # If checks pass, add triplets to the database and move images
        crud.create_labelized_triplets(db, triplets)

        for filename in uploaded_images:
            shutil.move(
                uploaded_images_path / filename,
                images_path / filename,
            )

        shutil.rmtree(uploaded_data_path)

        return JSONResponse(
            content={"message": "Data uploaded successfully."},
            status_code=status.HTTP_201_CREATED,
        )
    return None


@router.delete(
    "/delete_db",
    summary="Delete all the data inside the database.",
    status_code=status.HTTP_200_OK,
)
def delete_db(user: AdminUserSession, db: Session = Depends(get_db)) -> JSONResponse:
    crud.delete_all_data(db)
    return JSONResponse(
        content={"message": "Database deleted successfully."},
        status_code=status.HTTP_200_OK,
    )

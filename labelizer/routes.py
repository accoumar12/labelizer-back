import os
import shutil
import zipfile
from pathlib import Path
from config import get_app_config
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


# Dependency on the database
# todo to be moved
def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app_config = get_app_config()


@router.get(
    "/images/{image_id}",
    summary="Retrieve an image by its id.",
    status_code=status.HTTP_200_OK,
)
async def get_image(image_id: str) -> FileResponse:
    return FileResponse(f"{app_config.images_path}/{image_id}")


@router.get(
    "/triplet",
    summary="Get the triplet for the user of the app.",
    status_code=status.HTTP_200_OK,
)
def make_triplet(db: Session = Depends(get_db)) -> schemas.LabelizerTripletResponse:
    triplet = crud.get_first_unlabeled_triplet(db)
    if triplet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unlabeled triplet found.",
        )
    return schemas.LabelizerTripletResponse(
        id=triplet.id,
        reference_id=triplet.reference_id,
        reference_length=triplet.reference_length,
        left_id=triplet.left_id,
        left_length=triplet.reference_length,
        right_id=triplet.right_id,
        right_length=triplet.right_length,
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
    stream = get_db_excel_export(db)

    now = time.strftime("%Y%m%d-%H%M")
    filename = f"{now}_labelier_db.xlsx"

    return Response(
        content=stream.getvalue(),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def get_db_excel_export(db: Session) -> io.BytesIO:
    data = crud.get_all_data(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_excel(stream, index=False)
    stream.seek(0)
    return stream


@router.post(
    "/upload_data",
    summary="Upload new data, including images and triplets. The data has to be a zipped folder containing a csv file named triplets.csv and a folder named images containing the images. Needs to be authorized as an admin user.",
    status_code=status.HTTP_201_CREATED,
)
async def upload_data_endpoint(
    user: AdminUserSession,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    upload_data(file, db)

    return JSONResponse(
        content={"message": "Data uploaded successfully."},
        status_code=status.HTTP_201_CREATED,
    )


def upload_data(file: UploadFile, db) -> None:
    filename = file.filename
    if not filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file should be a zip file.",
        )

    extract_zip()

    tmp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(file.file, "r") as zip_ref:
        zip_ref.extractall(tmp_dir)

    uploaded_data_path = tmp_dir / "data"

    # Extract the csv file
    check_zip_format()

    if not Path(uploaded_data_path).exists():
        shutil.rmtree(tmp_dir)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The root folder in the zip file should be named 'data'.",
        )

    # Add the triplets to the database
    triplets_path = uploaded_data_path / "triplets.csv"
    if not triplets_path.exists():
        shutil.rmtree(uploaded_data_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The csv file should be named 'triplets.csv'.",
        )

    triplets = pd.read_csv(triplets_path)
    triplets_cads_ids = (
        triplets[["reference_id", "left_id", "right_id"]].to_numpy().flatten()
    )

    # Check if each value in the triplets corresponds to an image that is available (loaded + already there)
    uploaded_images_path = uploaded_data_path / "images"
    if not Path(uploaded_images_path).exists():
        shutil.rmtree(tmp_dir)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The images folder should exist and be named 'images'.",
        )

    check_images_availability()
    uploaded_images = set(uploaded_images_path.iterdir())
    uploaded_images_ids = {file.name.split(".")[0] for file in uploaded_images}
    all_images_ids = {
        file.name.split(".")[0] for file in app_config.images_path.iterdir()
    } | uploaded_images_ids
    triplet_values = set(triplets_cads_ids)

    missing_images_names = triplet_values - all_images_ids

    if missing_images_names:
        shutil.rmtree(uploaded_data_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing images for these triplets ids: {missing_images_names}.",
        )

    # If checks pass, add triplets to the database and move images

    update_database()

    crud.create_labelized_triplets(db, triplets)

    for file in uploaded_images:
        shutil.move(
            file,
            app_config.images_path / file.name,
        )

    shutil.rmtree(tmp_dir)


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

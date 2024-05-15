import shutil
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from labelizer import crud, schemas
from labelizer.app_config import get_app_config
from labelizer.core.api.auth.core import AdminUserSession, UserSession
from labelizer.core.database.get_database import get_db
from labelizer.types import SelectedItemType
from labelizer.utils import (
    check_structure_consistency,
    extract_zip,
    get_all_images_ids,
    get_db_excel_export,
    get_uploaded_images_ids,
    load_triplets,
    update_database,
)

router = APIRouter(tags=["Triplet Management"])

app_config = get_app_config()


@router.get(
    "/images/{image_id}",
    summary="Retrieve an image by its id. Needs the full path including the extension.",
    status_code=status.HTTP_200_OK,
)
async def get_image(image_id: str) -> FileResponse:
    return FileResponse(f"{app_config.images_path}/{image_id}.stp.png")


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


def upload_data(file: UploadFile, db: Session = Depends(get_db)) -> None:
    filename = file.filename
    if not filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file should be a zip file.",
        )

    tmp_path = extract_zip(file)

    uploaded_data_path = tmp_path / "data"
    check_structure_consistency(
        uploaded_data_path,
        tmp_path,
        "The zip file should contain a folder named 'data'.",
    )

    triplets_path = uploaded_data_path / "triplets.csv"
    check_structure_consistency(
        triplets_path,
        tmp_path,
        "The zip file should contain a csv file named 'triplets.csv'.",
    )

    # We need to load both the whole triplets (that contain all the data around triplets) and only the ids, that will be used to compare with the images
    triplets, triplets_ids = load_triplets(triplets_path)

    uploaded_images_path = uploaded_data_path / "images"
    check_structure_consistency(
        uploaded_images_path,
        tmp_path,
        "The data folder should contain a folder named 'images'.",
    )
    uploaded_images_ids = get_uploaded_images_ids(uploaded_images_path)
    all_images_ids = get_all_images_ids(uploaded_images_ids)

    # Check if for any triplet there will be a corresponding image
    missing_images_names = triplets_ids - all_images_ids
    if missing_images_names:
        shutil.rmtree(uploaded_data_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing images for these triplets ids: {missing_images_names}.",
        )

    # If checks pass, add triplets to the database and move images
    update_database(db, triplets, uploaded_images_path)
    shutil.rmtree(tmp_path)


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

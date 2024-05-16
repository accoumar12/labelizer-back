from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from labelizer import crud, schemas
from labelizer.app_config import get_app_config
from labelizer.core.api.auth.core import AdminUserSession, UserSession
from labelizer.core.api.logging import setup_logging
from labelizer.core.database.get_database import get_db
from labelizer.core.database.utils import (
    get_db_excel_export,
)
from labelizer.types import SelectedItemType
from labelizer.utils import upload_data

router = APIRouter(tags=["Triplet Management"])

app_config = get_app_config()

setup_logging(level=logging.INFO)


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
    logging.info("Image %s%s retrieved.", image_id, suffix)
    return FileResponse(f"{app_config.images_path}/{image_id}{suffix}.stp.png")


@router.get(
    "/triplet",
    summary="Get the triplet for the user of the app.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LabelizerTripletResponse
    | schemas.LabelizerValidationTripletResponse,
)
async def make_triplet(
    user: UserSession,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> schemas.LabelizerTripletResponse | schemas.LabelizerValidationTripletResponse:
    triplet = (
        crud.get_first_unlabeled_validation_triplet(db)
        if validation
        else crud.get_first_unlabeled_triplet(db)
    )
    if triplet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unlabeled triplet found.",
        )
    logging.info(
        "Validation Triplet %s retrieved.",
        triplet.id,
    ) if validation else logging.info("Triplet %s retrieved.", triplet.id)
    if validation:
        return schemas.LabelizerValidationTripletResponse(
            id=triplet.id,
            reference_id=triplet.reference_id,
            reference_length=triplet.reference_length,
            left_id=triplet.left_id,
            left_length=triplet.left_length,
            left_encoder_id=triplet.left_encoder_id,
            right_id=triplet.right_id,
            right_length=triplet.right_length,
            right_encoder_id=triplet.right_encoder_id,
        )
    return schemas.LabelizerTripletResponse(
        id=triplet.id,
        reference_id=triplet.reference_id,
        reference_length=triplet.reference_length,
        left_id=triplet.left_id,
        left_length=triplet.left_length,
        right_id=triplet.right_id,
        right_length=triplet.right_length,
    )


@router.get(
    "/triplet/stats",
    summary="Get the number of labeled and unlabeled triplets.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TripletStats,
)
async def get_triplet_stats(
    user: UserSession,
    db: Session = Depends(get_db),
) -> schemas.TripletStats:
    labeled_count = crud.count_labeled_triplets(db)
    unlabeled_count = crud.count_unlabeled_triplets(db)
    validation_labeled_count = crud.count_labeled_validation_triplets(db)
    validation_unlabeled_count = crud.count_unlabeled_validation_triplets(db)
    return schemas.TripletStats(
        labeled=labeled_count,
        unlabeled=unlabeled_count,
        validation_labeled=validation_labeled_count,
        validation_unlabeled=validation_unlabeled_count,
    )


@router.post(
    "/triplet",
    summary="Set the label of a triplet according to the user's choice.",
    status_code=status.HTTP_200_OK,
)
async def set_triplet_label(
    user: UserSession,
    triplet_id: str,
    label: SelectedItemType,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> JSONResponse:
    try:
        crud.set_validation_triplet_label(
            db,
            triplet_id,
            label,
            user.uid,
        ) if validation else crud.set_triplet_label(db, triplet_id, label, user.uid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    logging.info(
        " Validation Triplet %s labeled as %s.",
        triplet_id,
        label,
    ) if validation else logging.info("Triplet %s labeled as %s.", triplet_id, label)
    return JSONResponse(
        content={"message": "Label set successfully."},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/download_db",
    summary="Download all the database in the csv format. Needs to be authorized as an admin user.",
    status_code=status.HTTP_200_OK,
)
async def download_db(
    user: AdminUserSession,
    db: Session = Depends(get_db),
) -> FileResponse:
    stream = get_db_excel_export(db)

    now = time.strftime("%Y%m%d-%H%M")
    filename = f"{now}_labeliser_db.xlsx"

    logging.info("Database downloaded.")
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

    logging.info("Data uploaded.")
    return JSONResponse(
        content={"message": "Data uploaded successfully."},
        status_code=status.HTTP_201_CREATED,
    )


@router.delete(
    "/delete_db",
    summary="Delete all the data inside the database.",
    status_code=status.HTTP_200_OK,
)
async def delete_db(
    user: AdminUserSession,
    db: Session = Depends(get_db),
) -> JSONResponse:
    crud.delete_all_data(db)
    logging.info("Database deleted.")
    return JSONResponse(
        content={"message": "Database deleted successfully."},
        status_code=status.HTTP_200_OK,
    )

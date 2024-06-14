from __future__ import annotations

import io
import logging
import time

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from labelizer import crud, schemas
from labelizer.app_config import AppConfig
from labelizer.core.api.auth.core import AdminUserSession, UserSession
from labelizer.core.database.get_database import get_db
from labelizer.core.database.utils import (
    get_all_triplets_csv_stream,
    get_all_validation_triplets_csv_stream,
    upload_data,
)
from labelizer.types import SelectedItemType

router = APIRouter(tags=["Triplet Management"])

app_config = AppConfig()

logger = logging.getLogger()


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
    logger.info("Image %s%s retrieved.", image_id, suffix)
    return FileResponse(f"{app_config.images_path}/{image_id}{suffix}.stp.png")


@router.get(
    "/triplet",
    summary="Get the triplet for the user of the app.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LabelizerTripletResponse
    | schemas.LabelizerValidationTripletResponse,
)
async def get_triplet(
    user: UserSession,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> schemas.LabelizerTripletResponse | schemas.LabelizerValidationTripletResponse:
    if validation:
        triplet = crud.get_first_unlabeled_validation_triplet(db)
    else:
        triplet = crud.get_first_unlabeled_triplet(db)

    if triplet is None:
        logger.info("No unlabeled triplet found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unlabeled triplet found.",
        )
    if validation:
        logger.info("Validation Triplet %s retrieved.", triplet.id)
        return schemas.LabelizerValidationTripletResponse(
            id=triplet.id,
            reference_id=triplet.reference_id,
            reference_length=triplet.reference_item.length,
            left_id=triplet.left_id,
            left_length=triplet.left_item.length,
            left_encoder_id=triplet.left_encoder_id,
            right_id=triplet.right_id,
            right_length=triplet.right_item.length,
            right_encoder_id=triplet.right_encoder_id,
        )
    logger.info("Triplet %s retrieved.", triplet.id)
    return schemas.LabelizerTripletResponse(
        id=triplet.id,
        reference_id=triplet.reference_id,
        reference_length=triplet.reference_item.length,
        left_id=triplet.left_id,
        left_length=triplet.left_item.length,
        right_id=triplet.right_id,
        right_length=triplet.right_item.length,
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

    if validation:
        logger.info("Validation Triplet %s labeled as %s.", triplet_id, label)
    else:
        logger.info("Triplet %s labeled as %s.", triplet_id, label)
    return JSONResponse(
        content={"message": "Label set successfully."},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/upload_data",
    summary="Get the status of the last triplets data upload.",
)
async def get_upload_status(
    user: AdminUserSession,
    db: Session = Depends(get_db),
) -> schemas.TripletsUploadStatus:
    return crud.get_upload_status(db)


# We choose to upload both the triplets and validation triplets at once and not separately because we can easily define a format for the zipped folder
# Use of background tasks, might be replaced with celery if performance or scaling issues arise
@router.post(
    "/upload_data",
    summary="Upload new data, including images and triplets. The data has to be a zipped folder containing a csv file named triplets, a csv file named validation_triplets and a folder named images containing the images. Needs to be authorized as an admin user. If you do not want to include triplets, you can provide a csv file with no line but still the header.",
    status_code=status.HTTP_201_CREATED,
)
async def upload_data_in_the_background(
    user: AdminUserSession,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    # Read the file into memory
    file_in_memory = io.BytesIO(await file.read())

    # Add the task to the background with the file in memory
    background_tasks.add_task(upload_data, file_in_memory, db)
    logger.info("Data upload starts in the background.")
    return JSONResponse(
        content={"message": "Data upload starts in the background."},
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.get(
    "/download_db",
    summary="Download the database in the csv format.",
    status_code=status.HTTP_200_OK,
)
async def download_db(
    user: AdminUserSession,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> FileResponse:
    now = time.strftime("%Y%m%d-%H%M")
    if validation:
        stream = get_all_validation_triplets_csv_stream(db)
        filename = f"{now}_labelizer_validation_db.csv"
        logger.info("Validation database downloaded.")
    else:
        stream = get_all_triplets_csv_stream(db)
        filename = f"{now}_labelizer_db.csv"
        logger.info("Database downloaded.")
    return Response(
        content=stream.getvalue(),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        media_type="text/csv",
    )


@router.delete(
    "/delete_db",
    summary="Delete all the data inside the database.",
    status_code=status.HTTP_200_OK,
)
async def delete_db(
    user: AdminUserSession,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> JSONResponse:
    crud.delete_all_validation_triplets(db) if validation else crud.delete_all_triplets(
        db,
    )
    if validation:
        crud.delete_all_validation_triplets(db)
        logger.info("Validation database deleted.")
    else:
        crud.delete_all_triplets(db)
        logger.info("Database deleted.")
    return JSONResponse(
        content={"message": "Database deleted successfully."},
        status_code=status.HTTP_200_OK,
    )


# Not optimal to give the config this way, would be better to have a common config module to the backend and the frontend
@router.get(
    "/config",
    summary="Get some configuration variables of the app.",
)
def get_config() -> JSONResponse:
    return JSONResponse(
        content={
            "lock_timeout_in_seconds": app_config.lock_timeout_in_seconds,
        },
        status_code=status.HTTP_200_OK,
    )

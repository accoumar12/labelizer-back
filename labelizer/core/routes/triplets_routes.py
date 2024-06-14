from __future__ import annotations

import logging
import time

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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
)
from labelizer.types import SelectedItemType

triplets_router = APIRouter(tags=["Triplets"])

app_config = AppConfig()

logger = logging.getLogger()


@triplets_router.get(
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


@triplets_router.post(
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


@triplets_router.get(
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


# We choose to upload both the triplets and validation triplets at once and not separately because we can easily define a format for the zipped folder
# Use of background tasks, might be replaced with celery if performance or scaling issues arise
@triplets_router.get(
    "/download_db",
    summary="Download triplets data in the csv format.",
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


@triplets_router.delete(
    "/delete_db",
    summary="Delete triplets data inside the database.",
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


@triplets_router.get(
    "/upload_data",
    summary="Get the status of the last triplets data upload.",
)
async def get_upload_status(
    user: AdminUserSession,
    db: Session = Depends(get_db),
) -> schemas.TripletsUploadStatus:
    return crud.get_upload_status(db)

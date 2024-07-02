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

from backend.core.api.auth.core import AdminUserSession, UserSession
from backend.core.database.manage import get_db
from backend.triplets import crud, schemas
from backend.triplets.enums import SelectedItemType
from backend.triplets.flows import (
    get_triplets_csv_stream,
    get_validation_triplets_csv_stream,
)

router = APIRouter(tags=["Triplets"])

logger = logging.getLogger()


@router.get(
    "/triplet",
    summary="Get the triplet for the user of the app.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TripletResponse | schemas.ValidationTripletResponse,
)
async def get_triplet(
    user: UserSession,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> schemas.TripletResponse | schemas.ValidationTripletResponse:
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
        return schemas.ValidationTripletResponse(
            id=triplet.id,
            reference_id=triplet.reference_id,
            reference_length=triplet.reference_item.length,
            reference_dataset=triplet.reference_item.dataset,
            left_id=triplet.left_id,
            left_length=triplet.left_item.length,
            left_dataset=triplet.left_item.dataset,
            left_encoder_id=triplet.left_encoder_id,
            right_id=triplet.right_id,
            right_length=triplet.right_item.length,
            right_dataset=triplet.right_item.dataset,
            right_encoder_id=triplet.right_encoder_id,
        )
    logger.info("Triplet %s retrieved.", triplet.id)
    return schemas.TripletResponse(
        id=triplet.id,
        reference_id=triplet.reference_id,
        reference_length=triplet.reference_item.length,
        reference_dataset=triplet.reference_item.dataset,
        left_id=triplet.left_id,
        left_length=triplet.left_item.length,
        left_dataset=triplet.left_item.dataset,
        right_id=triplet.right_id,
        right_length=triplet.right_item.length,
        right_dataset=triplet.right_item.dataset,
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
    "/triplet/stats",
    summary="Get the number of labeled and unlabeled triplets.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TripletStats,
)
async def get_triplet_stats_endpoint(
    user: UserSession,
    db: Session = Depends(get_db),
) -> schemas.TripletStats:
    return crud.get_triplets_stats(db)


# We choose to upload both the triplets and validation triplets at once and not separately because we can easily define a format for the zipped folder
# Use of background tasks, might be replaced with celery if performance or scaling issues arise
@router.get(
    "/download",
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
        stream = get_validation_triplets_csv_stream(db)
        filename = f"{now}_backend_validation_triplets.csv"
        logger.info("Validation database downloaded.")
    else:
        stream = get_triplets_csv_stream(db)
        filename = f"{now}_backend_triplets.csv"
        logger.info("Database downloaded.")
    return Response(
        content=stream.getvalue(),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        media_type="text/csv",
    )


@router.delete(
    "/delete",
    summary="Delete triplets data inside the database.",
    status_code=status.HTTP_200_OK,
)
async def delete_db(
    user: AdminUserSession,
    validation: bool = False,
    db: Session = Depends(get_db),
) -> JSONResponse:
    crud.delete_validation_triplets(db) if validation else crud.delete_triplets(
        db,
    )
    if validation:
        crud.delete_validation_triplets(db)
        logger.info("Validation database deleted.")
    else:
        crud.delete_triplets(db)
        logger.info("Database deleted.")
    return JSONResponse(
        content={"message": "Database deleted successfully."},
        status_code=status.HTTP_200_OK,
    )

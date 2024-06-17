import io
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from labelizer.core.api.auth.core import AdminUserSession
from labelizer.core.database.get_database import get_db
from labelizer.upload.flows import upload_data

router = APIRouter(tags=["Upload"])

logger = logging.getLogger()


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

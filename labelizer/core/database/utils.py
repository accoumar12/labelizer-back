from __future__ import annotations

import io
import logging
import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from labelizer import crud
from labelizer.app_config import AppConfig
from labelizer.core.database.get_database import get_db

app_config = AppConfig()

logger = logging.getLogger()


def check_structure_consistency(
    path_to_be_present: Path,
    path_to_be_removed: Path,
    detail: str,
) -> None:
    if not path_to_be_present.exists():
        shutil.rmtree(path_to_be_removed)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def load_triplets(triplets_path: Path) -> pd.DataFrame:
    """Load triplets from a CSV file."""
    try:
        return pd.read_csv(triplets_path)
    except FileNotFoundError as e:
        logger.info("File not found: %s", e)
        return pd.DataFrame()


def extract_triplet_ids(triplets: pd.DataFrame) -> set[str]:
    """Extract a set of triplet IDs from a DataFrame."""
    return set(
        triplets[["reference_id", "left_id", "right_id"]].to_numpy().flatten(),
    )


def get_uploaded_images_ids(uploaded_images_path: Path) -> set[str]:
    uploaded_images = set(uploaded_images_path.iterdir())
    image_ids = {
        file.name.split(".")[0]
        for file in uploaded_images
        if not file.name.split(".")[0].endswith("_canonical")
    }
    canonical_image_ids = {
        file.name.split("_canonical")[0]
        for file in uploaded_images
        if file.name.split(".")[0].endswith("_canonical")
    }
    if image_ids != canonical_image_ids:
        # We have to use this method because we do not know which set is missing elements
        missing_canonicals = image_ids.symmetric_difference(canonical_image_ids)
        msg = f"Discrepancy between images and canonical images: {', '.join(missing_canonicals)}"
        raise ValueError(msg)
    return image_ids


def get_all_images_ids(uploaded_images_ids: set[str]) -> set[str]:
    # We use lazy evaluation to avoid checking the content of the images folder if it does not exist, then checking if it not empty to then iterate over it
    if not app_config.images_path.exists() or not any(app_config.images_path.iterdir()):
        return uploaded_images_ids
    return {
        file.name.split(".")[0]
        for file in app_config.images_path.iterdir()
        if not file.name.endswith("_canonical")
    } | uploaded_images_ids


def extract_zip(file_in_memory: io.BytesIO) -> Path:
    tmp_path = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(file_in_memory, "r") as zip_ref:
        zip_ref.extractall(tmp_path)
    return tmp_path


def upload_verified_data(
    file_in_memory: io.BytesIO,
    db: Session = Depends(get_db),
) -> None:
    logger.info("Verifying and Uploading data...")

    tmp_path = extract_zip(file_in_memory)
    logger.debug("Zip file extracted.")

    uploaded_data_path = tmp_path / "data"
    check_structure_consistency(
        uploaded_data_path,
        tmp_path,
        "The zip file should contain a folder named 'data'.",
    )

    uploaded_images_path = uploaded_data_path / "images"
    check_structure_consistency(
        uploaded_images_path,
        tmp_path,
        "The data folder should contain a folder named 'images'.",
    )
    uploaded_images_ids = get_uploaded_images_ids(uploaded_images_path)
    all_images_ids = get_all_images_ids(uploaded_images_ids)

    triplets_path = uploaded_data_path / "triplets.csv"
    check_structure_consistency(
        triplets_path,
        tmp_path,
        "The zip file should contain a csv file named 'triplets.csv'.",
    )

    triplets = load_triplets(triplets_path)
    logger.debug("Triplets loaded.")

    triplets_ids = extract_triplet_ids(triplets)
    check_match_triplets_images(triplets_ids, all_images_ids)
    logger.debug("Triplets images checked.")

    validation_triplets_path = uploaded_data_path / "validation_triplets.csv"
    check_structure_consistency(
        validation_triplets_path,
        tmp_path,
        "The zip file should contain a csv file named 'validation_triplets.csv'.",
    )

    validation_triplets = load_triplets(validation_triplets_path)
    logger.debug("Validation triplets loaded.")

    validation_triplets_ids = extract_triplet_ids(validation_triplets)
    check_match_triplets_images(validation_triplets_ids, all_images_ids)
    logger.debug("Validation triplets images checked.")

    crud.update_database(db, triplets, validation_triplets, uploaded_images_path)
    logger.info("Database updated")

    shutil.rmtree(tmp_path)
    logger.debug("Temporary files removed.")


def upload_data(file_in_memory: io.BytesIO, db: Session = Depends(get_db)) -> None:
    logger.info("Uploading data ...")

    tmp_path = extract_zip(file_in_memory)
    logger.debug("Zip file extracted.")

    uploaded_data_path = tmp_path / "data"

    triplets_path = uploaded_data_path / "triplets.csv"
    triplets = load_triplets(triplets_path)
    triplets_count = len(triplets)
    logger.debug("Triplets loaded.")

    validation_triplets_path = uploaded_data_path / "validation_triplets.csv"
    validation_triplets = load_triplets(validation_triplets_path)
    validation_triplets_count = len(validation_triplets)
    logger.debug("Validation triplets loaded.")

    all_triplets_count = triplets_count + validation_triplets_count
    # We create an entry in the database when we know how much triplets we have to upload
    crud.create_upload_status(db, all_triplets_count)

    uploaded_images_path = uploaded_data_path / "images"

    crud.update_database(
        db,
        triplets,
        validation_triplets,
        uploaded_images_path,
    )
    logger.info("Database updated")
    shutil.rmtree(tmp_path)


def check_match_triplets_images(
    triplets_ids: set[str],
    all_images_ids: set[str],
) -> None:
    missing_images_names = triplets_ids - all_images_ids
    if missing_images_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing images for these ids: {missing_images_names}.",
        )


def get_all_triplets_csv_stream(db: Session) -> io.BytesIO:
    data = crud.get_all_triplets(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_csv(stream, index=False)
    stream.seek(0)
    return stream


def get_all_validation_triplets_csv_stream(db: Session) -> io.BytesIO:
    data = crud.get_all_validation_triplets(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_csv(stream, index=False)
    stream.seek(0)
    return stream

from __future__ import annotations

import logging
import shutil
from typing import TYPE_CHECKING

import pandas as pd
from fastapi import Depends
from sqlalchemy.orm import Session

import backend.upload.crud
from backend.config.config import config
from backend.core.database.manage import get_db
from backend.items.crud import create_items
from backend.items.utils import load_items
from backend.triplets.crud import create_triplets, create_validation_triplets
from backend.triplets.utils import (
    check_match_triplets_images,
    extract_triplets_ids,
    load_triplets,
)
from backend.utils import (
    check_structure_consistency,
    extract_zip,
    get_all_images_ids,
    get_uploaded_images_ids,
)

if TYPE_CHECKING:
    import io
    from pathlib import Path

logger = logging.getLogger()


def update_database(
    db: Session,
    items: pd.DataFrame,
    triplets: pd.DataFrame,
    validation_triplets: pd.DataFrame,
    uploaded_images_path: Path,
) -> None:
    # Has to be done in this order because of foreign key constraints, which are not enforced with SQLite but are with PostgreSQL !
    if not items.empty:
        create_items(db, items)
    if not triplets.empty:
        create_triplets(db, triplets)
    if not validation_triplets.empty:
        create_validation_triplets(db, validation_triplets)
    uploaded_images = uploaded_images_path.iterdir()
    config.images_path.mkdir(parents=True, exist_ok=True)
    for file in uploaded_images:
        destination = config.images_path / file.name
        shutil.move(file, destination)
    logger.info("Database updated")


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

    triplets_ids = extract_triplets_ids(triplets)
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

    validation_triplets_ids = extract_triplets_ids(validation_triplets)
    check_match_triplets_images(validation_triplets_ids, all_images_ids)
    logger.debug("Validation triplets images checked.")

    update_database(
        db,
        triplets,
        validation_triplets,
        uploaded_images_path,
    )
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
    backend.upload.crud.create_upload_status(db, all_triplets_count)

    items = load_items(uploaded_data_path / "items.csv")
    logger.debug("Items loaded.")

    uploaded_images_path = uploaded_data_path / "images"

    update_database(
        db,
        items,
        triplets,
        validation_triplets,
        uploaded_images_path,
    )
    shutil.rmtree(tmp_path)
    logging.info("Temporary files removed.")

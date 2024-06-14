from __future__ import annotations

import datetime
import logging
import shutil
from typing import TYPE_CHECKING

from labelizer import models, schemas
from labelizer.app_config import AppConfig

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd
    from sqlalchemy.orm import Session

    from labelizer.crud import SelectedItemType

app_config = AppConfig()

logger = logging.getLogger()


# We get last status, because we are not going to upload data at the same time... Might cause an issue if several downloads are done at the same time
def increment_triplets_upload_status(
    db: Session,
) -> None:
    status = (
        db.query(models.TripletUploadStatus)
        .order_by(models.TripletUploadStatus.id.desc())
        .first()
    )
    status.uploaded_triplets_count += 1
    db.commit()


def create_labeled_triplet(
    db: Session,
    triplet: schemas.LabeledTriplet,
) -> models.LabeledTriplet:
    db_triplet = models.LabeledTriplet(**triplet.model_dump())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    logging.debug("Labeled triplet added to the database.")
    increment_triplets_upload_status(db)
    return db_triplet


def create_validation_triplet(
    db: Session,
    triplet: schemas.ValidationTriplet,
) -> models.ValidationTriplet:
    db_triplet = models.ValidationTriplet(**triplet.model_dump())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    increment_triplets_upload_status(db)
    return db_triplet


def create_item(
    db: Session,
    item: schemas.Item,
) -> models.Item:
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_labeled_triplets(
    db: Session,
    triplets: pd.DataFrame,
) -> None:
    for _, triplet in triplets.iterrows():
        create_labeled_triplet(
            db,
            schemas.LabeledTriplet(**triplet.to_dict()),
        )
    logger.debug("Labeled triplets added to the database.")


def create_validation_triplets(
    db: Session,
    triplets: pd.DataFrame,
) -> None:
    for _, triplet in triplets.iterrows():
        create_validation_triplet(
            db,
            schemas.ValidationTriplet(**triplet.to_dict()),
        )
    logger.debug("Validation triplets added to the database.")


def create_items(
    db: Session,
    items: pd.DataFrame,
) -> None:
    for _, item in items.iterrows():
        create_item(
            db,
            schemas.Item(**item.to_dict()),
        )


# We make sure two users do not label the same triplet by implementing our own locking mechanism. Not ideal because after the timeout period the triplet will be considered as "unlocked" and could be retrieved by another user.
def get_first_unlabeled_triplet(
    db: Session,
    lock_timeout_in_seconds: int = app_config.lock_timeout_in_seconds,
) -> models.LabeledTriplet:
    now_time = datetime.datetime.now(datetime.timezone.utc)
    # We define the timeout as the current time minus the lock_timeout_in_seconds, so the boundary, cutoff below which the triplet is considered as "unlocked", "stale"
    cutoff_time = now_time - datetime.timedelta(
        seconds=lock_timeout_in_seconds,
    )
    # We retrieve the first triplet that is unlabeled and either has never been retrieved or has been retrieved before the cutoff time
    triplet = (
        db.query(models.LabeledTriplet)
        .filter(
            (models.LabeledTriplet.label.is_(None))
            & (
                (models.LabeledTriplet.retrieved_at.is_(None))
                | (models.LabeledTriplet.retrieved_at < cutoff_time)
            ),
        )
        .first()
    )
    if triplet:
        triplet.retrieved_at = now_time
        db.commit()
    return triplet


def get_first_unlabeled_validation_triplet(
    db: Session,
    lock_timeout_in_seconds: int = app_config.lock_timeout_in_seconds,
) -> models.ValidationTriplet:
    now_time = datetime.datetime.now(datetime.timezone.utc)
    cutoff_time = now_time - datetime.timedelta(
        seconds=lock_timeout_in_seconds,
    )
    triplet = (
        db.query(models.ValidationTriplet)
        .filter(
            (models.ValidationTriplet.label.is_(None))
            & (
                (models.ValidationTriplet.retrieved_at.is_(None))
                | (models.ValidationTriplet.retrieved_at < cutoff_time)
            ),
        )
        .first()
    )
    if triplet:
        triplet.retrieved_at = now_time
        db.commit()
    return triplet


def count_labeled_triplets(db: Session) -> int:
    return (
        db.query(models.LabeledTriplet)
        .filter(models.LabeledTriplet.label.isnot(None))
        .count()
    )


def count_labeled_validation_triplets(db: Session) -> int:
    return (
        db.query(models.ValidationTriplet)
        .filter(models.ValidationTriplet.label.isnot(None))
        .count()
    )


def count_unlabeled_triplets(db: Session) -> int:
    return (
        db.query(models.LabeledTriplet)
        .filter(models.LabeledTriplet.label.is_(None))
        .count()
    )


def count_unlabeled_validation_triplets(db: Session) -> int:
    return (
        db.query(models.ValidationTriplet)
        .filter(models.ValidationTriplet.label.is_(None))
        .count()
    )


def set_triplet_label(
    db: Session,
    triplet_id: int,
    label: SelectedItemType,
    user_id: str,
) -> None:
    triplet = (
        db.query(models.LabeledTriplet)
        .filter(models.LabeledTriplet.id == triplet_id)
        .first()
    )
    if triplet is None:
        msg = f"No triplet found with id {triplet_id}"
        raise ValueError(msg)
    triplet.label = label
    triplet.user_id = user_id
    db.commit()


def set_validation_triplet_label(
    db: Session,
    triplet_id: int,
    label: SelectedItemType,
    user_id: str,
) -> None:
    triplet = (
        db.query(models.ValidationTriplet)
        .filter(models.ValidationTriplet.id == triplet_id)
        .first()
    )
    if triplet is None:
        msg = f"No validation triplet found with id {triplet_id}"
        raise ValueError(msg)
    triplet.label = label
    triplet.user_id = user_id
    db.commit()


# We only retrieve the triplets that have been labeled
def get_all_triplets(db: Session) -> list[dict]:
    return [
        triplet.to_dict()
        for triplet in db.query(models.LabeledTriplet)
        .filter(models.LabeledTriplet.label.isnot(None))
        .all()
    ]


def get_all_validation_triplets(db: Session) -> list[dict]:
    return [
        triplet.to_dict()
        for triplet in db.query(models.ValidationTriplet)
        .filter(models.ValidationTriplet.label.isnot(None))
        .all()
    ]


def delete_all_triplets(db: Session) -> None:
    db.query(models.LabeledTriplet).delete()
    db.commit()


def delete_all_validation_triplets(db: Session) -> None:
    db.query(models.ValidationTriplet).delete()
    db.commit()


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
        create_labeled_triplets(db, triplets)
    if not validation_triplets.empty:
        create_validation_triplets(db, validation_triplets)
    uploaded_images = uploaded_images_path.iterdir()
    app_config.images_path.mkdir(parents=True, exist_ok=True)
    for file in uploaded_images:
        destination = app_config.images_path / file.name
        shutil.move(file, destination)


def create_upload_status(
    db: Session,
    to_upload_triplets_count: int,
) -> models.TripletUploadStatus:
    db_status = models.TripletUploadStatus(
        to_upload_triplets_count=to_upload_triplets_count,
        uploaded_triplets_count=0,
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


def get_upload_status(
    db: Session,
) -> models.TripletUploadStatus:
    upload_status = (
        db.query(models.TripletUploadStatus)
        .order_by(models.TripletUploadStatus.id.desc())
        .first()
    )
    if upload_status is None:
        # Return a default TripletUploadStatus object when there is no record in the database, because we experienced a bug when no data was uploaded yet
        return models.TripletUploadStatus(
            id=0,
            to_upload_triplets_count=0,
            uploaded_triplets_count=0,
        )
    return upload_status

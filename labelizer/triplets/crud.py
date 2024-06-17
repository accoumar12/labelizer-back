from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING

import labelizer.triplets.models
import labelizer.triplets.schemas
from labelizer.config.app_config import app_config
from labelizer.triplets.enums import SelectedItemType

if TYPE_CHECKING:
    import pandas as pd
    from sqlalchemy.orm import Session


logger = logging.getLogger()


# We get last status, because we are not going to upload data at the same time... Might cause an issue if several downloads are done at the same time
def increment_triplets_upload_status(
    db: Session,
) -> None:
    status = (
        db.query(labelizer.triplets.models.TripletUploadStatus)
        .order_by(labelizer.triplets.models.TripletUploadStatus.id.desc())
        .first()
    )
    status.uploaded_triplets_count += 1
    db.commit()


def create_labeled_triplet(
    db: Session,
    triplet: labelizer.triplets.schemas.LabeledTriplet,
) -> labelizer.triplets.models.LabeledTriplet:
    triplet = labelizer.triplets.models.LabeledTriplet(**triplet.model_dump())
    db.add(triplet)
    db.commit()
    db.refresh(triplet)
    logger.debug("Labeled triplet added to the database.")
    increment_triplets_upload_status(db)
    return triplet


def create_validation_triplet(
    db: Session,
    triplet: labelizer.triplets.schemas.ValidationTriplet,
) -> labelizer.triplets.models.ValidationTriplet:
    triplet = labelizer.triplets.models.ValidationTriplet(**triplet.model_dump())
    db.add(triplet)
    db.commit()
    db.refresh(triplet)
    logger.debug("Validation triplet added to the database.")
    increment_triplets_upload_status(db)
    return triplet


def create_labeled_triplets(
    db: Session,
    triplets: pd.DataFrame,
) -> None:
    for _, triplet in triplets.iterrows():
        create_labeled_triplet(
            db,
            labelizer.triplets.schemas.LabeledTriplet(**triplet.to_dict()),
        )
    logger.debug("Labeled triplets added to the database.")


def create_validation_triplets(
    db: Session,
    triplets: pd.DataFrame,
) -> None:
    for _, triplet in triplets.iterrows():
        create_validation_triplet(
            db,
            labelizer.triplets.schemas.ValidationTriplet(**triplet.to_dict()),
        )
    logger.debug("Validation triplets added to the database.")


# We make sure two users do not label the same triplet by implementing our own locking mechanism. Not ideal because after the timeout period the triplet will be considered as "unlocked" and could be retrieved by another user.
def get_first_unlabeled_triplet(
    db: Session,
    lock_timeout_in_seconds: int = app_config.lock_timeout_in_seconds,
) -> labelizer.triplets.models.LabeledTriplet:
    now_time = datetime.datetime.now(datetime.timezone.utc)
    # We define the timeout as the current time minus the lock_timeout_in_seconds, so the boundary, cutoff below which the triplet is considered as "unlocked", "stale"
    cutoff_time = now_time - datetime.timedelta(
        seconds=lock_timeout_in_seconds,
    )
    # We retrieve the first triplet that is unlabeled and either has never been retrieved or has been retrieved before the cutoff time
    triplet = (
        db.query(labelizer.triplets.models.LabeledTriplet)
        .filter(
            (labelizer.triplets.models.LabeledTriplet.label.is_(None))
            & (
                (labelizer.triplets.models.LabeledTriplet.retrieved_at.is_(None))
                | (labelizer.triplets.models.LabeledTriplet.retrieved_at < cutoff_time)
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
) -> labelizer.triplets.models.ValidationTriplet:
    now_time = datetime.datetime.now(datetime.timezone.utc)
    cutoff_time = now_time - datetime.timedelta(
        seconds=lock_timeout_in_seconds,
    )
    triplet = (
        db.query(labelizer.triplets.models.ValidationTriplet)
        .filter(
            (labelizer.triplets.models.ValidationTriplet.label.is_(None))
            & (
                (labelizer.triplets.models.ValidationTriplet.retrieved_at.is_(None))
                | (
                    labelizer.triplets.models.ValidationTriplet.retrieved_at
                    < cutoff_time
                )
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
        db.query(labelizer.triplets.models.LabeledTriplet)
        .filter(labelizer.triplets.models.LabeledTriplet.label.isnot(None))
        .count()
    )


def count_labeled_validation_triplets(db: Session) -> int:
    return (
        db.query(labelizer.triplets.models.ValidationTriplet)
        .filter(labelizer.triplets.models.ValidationTriplet.label.isnot(None))
        .count()
    )


def count_unlabeled_triplets(db: Session) -> int:
    return (
        db.query(labelizer.triplets.models.LabeledTriplet)
        .filter(labelizer.triplets.models.LabeledTriplet.label.is_(None))
        .count()
    )


def count_unlabeled_validation_triplets(db: Session) -> int:
    return (
        db.query(labelizer.triplets.models.ValidationTriplet)
        .filter(labelizer.triplets.models.ValidationTriplet.label.is_(None))
        .count()
    )


def set_triplet_label(
    db: Session,
    triplet_id: int,
    label: SelectedItemType,
    user_id: str,
) -> None:
    triplet = (
        db.query(labelizer.triplets.models.LabeledTriplet)
        .filter(labelizer.triplets.models.LabeledTriplet.id == triplet_id)
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
        db.query(labelizer.triplets.models.ValidationTriplet)
        .filter(labelizer.triplets.models.ValidationTriplet.id == triplet_id)
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
        for triplet in db.query(labelizer.triplets.models.LabeledTriplet)
        .filter(labelizer.triplets.models.LabeledTriplet.label.isnot(None))
        .all()
    ]


def get_all_validation_triplets(db: Session) -> list[dict]:
    return [
        triplet.to_dict()
        for triplet in db.query(labelizer.triplets.models.ValidationTriplet)
        .filter(labelizer.triplets.models.ValidationTriplet.label.isnot(None))
        .all()
    ]


def delete_all_triplets(db: Session) -> None:
    db.query(labelizer.triplets.models.LabeledTriplet).delete()
    db.commit()


def delete_all_validation_triplets(db: Session) -> None:
    db.query(labelizer.triplets.models.ValidationTriplet).delete()
    db.commit()

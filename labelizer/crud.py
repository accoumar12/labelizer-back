from __future__ import annotations

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


def create_labelized_triplet(
    db: Session,
    triplet: schemas.LabelizedTriplet,
) -> models.LabelizedTriplet:
    db_triplet = models.LabelizedTriplet(**triplet.model_dump())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet


def create_validation_triplet(
    db: Session,
    triplet: schemas.ValidationTriplet,
) -> models.ValidationTriplet:
    db_triplet = models.ValidationTriplet(**triplet.model_dump())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet


def create_labelized_triplets(db: Session, triplets: pd.DataFrame) -> None:
    for _, triplet in triplets.iterrows():
        create_labelized_triplet(db, schemas.LabelizedTriplet(**triplet.to_dict()))


def create_validation_triplets(db: Session, triplets: pd.DataFrame) -> None:
    for _, triplet in triplets.iterrows():
        create_validation_triplet(db, schemas.ValidationTriplet(**triplet.to_dict()))


def get_first_unlabeled_triplet(db: Session) -> models.LabelizedTriplet:
    return (
        db.query(models.LabelizedTriplet)
        .filter(models.LabelizedTriplet.label.is_(None))
        .first()
    )


def get_first_unlabeled_validation_triplet(db: Session) -> models.ValidationTriplet:
    return (
        db.query(models.ValidationTriplet)
        .filter(models.ValidationTriplet.label.is_(None))
        .first()
    )


def count_labeled_triplets(db: Session) -> int:
    return (
        db.query(models.LabelizedTriplet)
        .filter(models.LabelizedTriplet.label.isnot(None))
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
        db.query(models.LabelizedTriplet)
        .filter(models.LabelizedTriplet.label.is_(None))
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
        db.query(models.LabelizedTriplet)
        .filter(models.LabelizedTriplet.id == triplet_id)
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


def get_all_triplets(db: Session) -> list[dict]:
    return [triplet.to_dict() for triplet in db.query(models.LabelizedTriplet).all()]


def get_all_validation_triplets(db: Session) -> list[dict]:
    return [triplet.to_dict() for triplet in db.query(models.ValidationTriplet).all()]


def delete_all_data(db: Session) -> None:
    db.query(models.LabelizedTriplet).delete()
    db.commit()


def update_database(
    db: Session,
    triplets: pd.DataFrame,
    validation_triplets: pd.DataFrame,
    uploaded_images_path: Path,
) -> None:
    create_labelized_triplets(db, triplets)
    create_validation_triplets(db, validation_triplets)
    uploaded_images = uploaded_images_path.iterdir()
    app_config.images_path.mkdir(parents=True, exist_ok=True)
    for file in uploaded_images:
        destination = app_config.images_path / file.name
        shutil.move(file, destination)

from __future__ import annotations

from typing import TYPE_CHECKING

from labelizer import models, schemas

if TYPE_CHECKING:
    import pandas as pd
    from sqlalchemy.orm import Session

    from labelizer.utils import SelectedItemType


def create_labelized_triplet(
    db: Session,
    triplet: schemas.LabelizedTriplet,
) -> models.LabelizedTriplet:
    db_triplet = models.LabelizedTriplet(**triplet.dict())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet


def create_labelized_triplets(db: Session, triplets: pd.DataFrame) -> None:
    for _, triplet in triplets.iterrows():
        create_labelized_triplet(db, schemas.LabelizedTriplet(**triplet.to_dict()))


def get_first_unlabeled_triplet(db: Session) -> models.LabelizedTriplet:
    return (
        db.query(models.LabelizedTriplet)
        .filter(models.LabelizedTriplet.label.is_(None))
        .first()
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


def get_all_data(db: Session) -> list[dict]:
    return [triplet.to_dict() for triplet in db.query(models.LabelizedTriplet).all()]


def delete_all_data(db: Session) -> None:
    db.query(models.LabelizedTriplet).delete()
    db.commit()

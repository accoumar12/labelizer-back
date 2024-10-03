import logging

import pandas as pd
from sqlalchemy.orm import Session

from backend.items import models, schemas


def create_item(
    db: Session,
    item: schemas.Item,
) -> models.Item:
    existing_item = db.query(models.Item).filter_by(id=item.id).first()
    if existing_item:
        logging.info("Item with id %s already exists.", item.id)
        return None
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item(
    db: Session,
    item_id: str,
) -> models.Item:
    return db.query(models.Item).filter_by(id=item_id).first()


def create_items(
    db: Session,
    items: pd.DataFrame,
) -> None:
    for _, item in items.iterrows():
        create_item(
            db,
            schemas.Item(**item.to_dict()),
        )

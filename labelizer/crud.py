from sqlalchemy.orm import Session

from labelizer import models, schemas
from labelizer.utils import SelectedItemType


def create_labelized_triplet(db: Session, triplet: schemas.LabelizedTriplet):
    db_triplet = models.LabelizedTriplet(**triplet.dict())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet

def get_first_unlabeled_triplet(db: Session):
    return db.query(models.LabelizedTriplet).filter(models.LabelizedTriplet.label.is_(None)).first()

def set_triplet_label(db: Session, triplet_id: int, label: SelectedItemType):
    triplet = db.query(models.LabelizedTriplet).filter(models.LabelizedTriplet.id == triplet_id).first()
    if triplet is None:
        raise ValueError(f"No triplet found with id {triplet_id}")
    triplet.label = label
    db.commit()
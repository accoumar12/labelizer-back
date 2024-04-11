from sqlalchemy.orm import Session

from . import models, schemas


def get_labelized_triplet(db: Session, triplet_id: int):
    return db.query(models.LabelizedTriplet).filter(models.LabelizedTriplet.id == triplet_id).first()

def create_labelized_triplet(db: Session, triplet: schemas.LabelizedTriplet):
    db_triplet = models.LabelizedTriplet(**triplet.dict())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet
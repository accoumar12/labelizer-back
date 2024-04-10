from sqlalchemy.orm import Session

from . import models, schemas


def get_labelized_triplet(db: Session, triplet_id: int):
    return db.query(models.TripletLabelized).filter(models.TripletLabelized.id == triplet_id).first()

def create_labelized_triplet(db: Session, triplet: schemas.TripletLabelized):
    db_triplet = models.TripletLabelized(**triplet.dict())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet

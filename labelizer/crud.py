from sqlalchemy.orm import Session

from labelizer import models, schemas


def create_labelized_triplet(db: Session, triplet: schemas.LabelizedTriplet):
    db_triplet = models.LabelizedTriplet(**triplet.dict())
    db.add(db_triplet)
    db.commit()
    db.refresh(db_triplet)
    return db_triplet

def get_first_unlabeled_triplet(db: Session):
    return db.query(models.LabelizedTriplet).filter(models.LabelizedTriplet.label.is_(None)).first()

# def update_labelized_triplet(db: Session, user_id: str, request_id: str, label: SelectedItemType):
#     db_triplet = db.query(LabelizedTriplet).filter(LabelizedTriplet.user_id == user_id, LabelizedTriplet.request_id == request_id).first()
#     if db_triplet is not None:
#         db_triplet.label = label
#         db.commit()
#         db.refresh(db_triplet)
#     return db_triplet

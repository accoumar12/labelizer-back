from sqlalchemy.orm import Session

from labelizer.upload import models, schemas


def create_upload_status(
    db: Session,
    to_upload_triplets_count: int,
) -> models.AllTripletsUploadStatus:
    db_status = models.AllTripletsUploadStatus(
        to_upload_all_triplets_count=to_upload_triplets_count,
        uploaded_all_triplets_count=0,
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


def get_upload_status(
    db: Session,
) -> models.AllTripletsUploadStatus:
    upload_status = (
        db.query(models.AllTripletsUploadStatus)
        .order_by(models.AllTripletsUploadStatus.id.desc())
        .first()
    )
    if upload_status is None:
        # Return a default TripletUploadStatus object when there is no record in the database, because we experienced a bug when no data was uploaded yet
        return schemas.AllTripletsUploadStatus(
            id=0,
            to_upload_all_triplets_count=0,
            uploaded_all_triplets_count=0,
        )
    return upload_status

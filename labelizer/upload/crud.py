from sqlalchemy.orm import Session

import labelizer.triplets.models


def create_upload_status(
    db: Session,
    to_upload_triplets_count: int,
) -> labelizer.triplets.models.TripletUploadStatus:
    db_status = labelizer.triplets.models.TripletUploadStatus(
        to_upload_triplets_count=to_upload_triplets_count,
        uploaded_triplets_count=0,
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


def get_upload_status(
    db: Session,
) -> labelizer.triplets.models.TripletUploadStatus:
    upload_status = (
        db.query(labelizer.triplets.models.TripletUploadStatus)
        .order_by(labelizer.triplets.models.TripletUploadStatus.id.desc())
        .first()
    )
    if upload_status is None:
        # Return a default TripletUploadStatus object when there is no record in the database, because we experienced a bug when no data was uploaded yet
        return labelizer.triplets.models.TripletUploadStatus(
            id=0,
            to_upload_triplets_count=0,
            uploaded_triplets_count=0,
        )
    return upload_status

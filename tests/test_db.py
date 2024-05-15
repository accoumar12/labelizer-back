from labelizer.core.database.init_database import SessionLocal


def test_create_labelized_triplet():
    db = SessionLocal()
    try:
        triplet = schemas.LabelizedTriplet(reference_id="1", left_id="1", right_id="1")
        result = crud.create_labelized_triplet(db, triplet)
        assert result.reference_id == "1"
    finally:
        db.rollback()

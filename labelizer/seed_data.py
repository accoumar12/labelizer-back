from labelizer import crud, schemas
from labelizer.core.database.init_database import SessionLocal


def seed_data():
    db = SessionLocal()

    triplet1 = schemas.LabelizedTriplet(
        reference_id="1",
        left_id="1",
        right_id="1",
    )

    triplet2 = schemas.LabelizedTriplet(
        reference_id="2",
        left_id="2",
        right_id="2",
    )

    triplet3 = schemas.LabelizedTriplet(
        reference_id="3",
        left_id="3",
        right_id="3",
    )

    # Use the crud functions to add them to the database
    crud.create_labelized_triplet(db, triplet1)
    crud.create_labelized_triplet(db, triplet2)
    crud.create_labelized_triplet(db, triplet3)

if __name__ == "__main__":
    seed_data()
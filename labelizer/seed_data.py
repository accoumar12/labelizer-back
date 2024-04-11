from labelizer import crud, models
from labelizer.core.database.init_database import SessionLocal


def seed_data():
    db = SessionLocal()

    triplet1 = models.LabelizedTriplet(
        reference_id="1",
        left_id="1",
        right_id="1",
        label=None,
        user_id="1"
    )

    triplet2 = models.LabelizedTriplet(
        reference_id="2",
        left_id="2",
        right_id="2",
        label=None,
        user_id="2"
    )

    # Use the crud functions to add them to the database
    crud.create_labelized_triplet(db, triplet1)
    crud.create_labelized_triplet(db, triplet2)

if __name__ == "__main__":
    seed_data()
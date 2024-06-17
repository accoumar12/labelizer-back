from unittest.mock import Mock, patch

import pandas as pd
from sqlalchemy.orm import Session

from labelizer.triplets import crud, models, schemas


def test_create_labeled_triplet() -> None:
    db = Mock(spec=Session)
    triplet = schemas.LabeledTriplet(
        reference_id="1",
        reference_length=1,
        left_id="1",
        left_length=1,
        right_id="1",
        right_length=1,
        encoder_id="1",
    )

    result = crud.create_labeled_triplet(db, triplet)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, models.LabeledTriplet)


def test_create_labeled_triplets() -> None:
    db = Mock(spec=Session)
    triplets = pd.DataFrame(
        [
            {
                "reference_id": "1",
                "reference_length": 1,
                "left_id": "1",
                "left_length": 1,
                "right_id": "1",
                "right_length": 1,
                "encoder_id": "1",
            },
        ],
    )

    with patch("labelizer.crud.create_labeled_triplet") as mock_create_triplet:
        crud.create_labeled_triplets(db, triplets)
        mock_create_triplet.assert_called_once()


def test_set_triplet_label() -> None:
    db = Mock(spec=Session)
    triplet_id = 1
    label = "label"
    user_id = "user_id"

    with patch("labelizer.crud.models.LabeledTriplet") as mock_triplet:
        crud.set_triplet_label(db, triplet_id, label, user_id)
        db.query.assert_called_once_with(mock_triplet)

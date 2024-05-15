from unittest.mock import Mock, patch

import pandas as pd
from sqlalchemy.orm import Session

from labelizer import crud, models, schemas


def test_create_labelized_triplet() -> None:
    db = Mock(spec=Session)
    triplet = schemas.LabelizedTriplet(reference_id="1", left_id="1", right_id="1")

    result = crud.create_labelized_triplet(db, triplet)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert isinstance(result, models.LabelizedTriplet)


def test_create_labelized_triplets() -> None:
    db = Mock(spec=Session)
    triplets = pd.DataFrame([{"reference_id": "1", "left_id": "1", "right_id": "1"}])

    with patch("labelizer.crud.create_labelized_triplet") as mock_create_triplet:
        crud.create_labelized_triplets(db, triplets)
        mock_create_triplet.assert_called_once()


# def test_get_first_unlabeled_triplet():
#     db = Mock(spec=Session)
#     db.query().filter().first.return_value = models.LabelizedTriplet()

#     result = crud.get_first_unlabeled_triplet(db)

#     db.query.assert_called_once_with(models.LabelizedTriplet)
#     db.query().filter.assert_called_once_with(models.LabelizedTriplet.label.is_(None))
#     assert isinstance(result, models.LabelizedTriplet)


def test_set_triplet_label() -> None:
    db = Mock(spec=Session)
    triplet_id = 1
    label = "label"
    user_id = "user_id"

    with patch("labelizer.crud.models.LabelizedTriplet") as mock_triplet:
        crud.set_triplet_label(db, triplet_id, label, user_id)
        db.query.assert_called_once_with(mock_triplet)

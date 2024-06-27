from backend.items.models import Item
from backend.triplets.models import Triplet, ValidationTriplet

test_item = Item(id="test-id", length=1.0, dataset="test-dataset")

test_triplet = Triplet(
    encoder_id="test-encoder-id",
    reference_id="test-id",
    left_id="test-id",
    right_id="test-id",
)

test_validation_triplet = ValidationTriplet(
    left_encoder_id="test-encoder-id",
    right_encoder_id="test-encoder-id",
    reference_id="test-id",
    left_id="test-id",
    right_id="test-id",
)

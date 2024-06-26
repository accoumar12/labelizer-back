from fastapi import APIRouter, Depends
from backend.core.database.manage import get_db
from backend.similarity.flows import compute_similarity_score, get_nearest_neighbors
from sqlalchemy.orm import Session

router = APIRouter(tags=["Similarity"])


@router.get(
    "/similarity/{item1_id}/{item2_id}",
    summary="Compute a cosine similarity score between two items.",
    status_code=200,
)
def compute_similarity_score_endpoint(
    item1_id: str,
    item2_id: str,
    db: Session = Depends(get_db),
) -> dict:
    return compute_similarity_score(item1_id, item2_id, db)


# By default, pgvector performs exact neighbor search. This is what we want here, if we want to approximate the search we might consider indexing the vectors as explained in the docs.
@router.get(
    "/neighbors/{item_id}",
    summary="Get the nearest neighbors of an item.",
    status_code=200,
)
def get_nearest_neighbors_endpoint(
    item_id: str,
    nearest_neighbors_count: int,
    db: Session = Depends(get_db),
) -> dict:
    return get_nearest_neighbors(item_id, nearest_neighbors_count, db)

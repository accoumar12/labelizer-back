from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from labelizer import crud
from labelizer.core.database.get_database import get_db
from labelizer.models import Item

similarity_router = APIRouter(tags=["Similarity"])


@similarity_router.get("/similarity/{item1_id}/{item2_id}")
def compute_similarity(
    item1_id: str,
    item2_id: str,
    db: Session = Depends(get_db),
) -> dict:
    item1 = crud.get_item(db, item1_id)
    item2 = crud.get_item(db, item2_id)
    if item1 is None or item2 is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item2_vector = str(item2.vector.tolist())  # Convert numpy array to list
    similarity_score = db.execute(
        text(
            "SELECT (vector <=> :item2_vector) FROM items WHERE id = :item1_id",
        ),
        {"item2_vector": item2_vector, "item1_id": item1.id},
    ).scalar()
    return {"similarity_score": similarity_score}


# By default, pgvector performs exact neighbor search. This is what we want here, if we want to approximate the search we might consider indexing the vectors as explained in the docs.
@similarity_router.get("/neighbors/{item_id}")
def get_nearest_neighbors(
    item_id: str,
    nearest_neighbors_count: int,
    db: Session = Depends(get_db),
):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    neighbors = (
        db.execute(
            select(Item)
            .order_by(Item.vector.cosine_distance(item.vector))
            .limit(nearest_neighbors_count),
        )
        .scalars()
        .all()
    )
    return {"neighbors": [neighbor.id for neighbor in neighbors]}

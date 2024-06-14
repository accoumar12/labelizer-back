from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from labelizer import crud
from labelizer.core.database.get_database import get_db

similarity_router = APIRouter(tags=["Similarity"])


@similarity_router.get("/similarity/{item1_id}/{item2_id}")
def compute_similarity(item1_id: int, item2_id: int, db: Session = Depends(get_db)):
    item1 = crud.get_item(db, item1_id)
    item2 = crud.get_item(db, item2_id)
    if item1 is None or item2 is None:
        raise HTTPException(status_code=404, detail="Item not found")
    similarity_score = item1.vector.cosine_similarity(item2.vector)
    return {"similarity_score": similarity_score}


# By default, pgvector performs exact neighbor search. This is what we want here, if we want to approximate the search we might consider indexing the vectors as explained in the docs.
@similarity_router.get("/neighbors/{item_id}")
def get_nearest_neighbors(
    item_id: int,
    nearest_neighbors_count: int,
    db: Session = Depends(get_db),
):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    neighbors = db.query(crud.Item).filter(
        crud.Item.vector.nearest_neighbor(item.vector, nearest_neighbors_count),
    )
    return {"neighbors": [neighbor.id for neighbor in neighbors]}

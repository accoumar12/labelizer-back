from fastapi import Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.core.database.manage import get_db
from backend.items import crud
from backend.items.models import Item


def compute_similarity_score(
    item1_id: str,
    item2_id: str,
    db: Session = Depends(get_db),
) -> dict:
    item1 = crud.get_item(db, item1_id)
    item2 = crud.get_item(db, item2_id)
    if item1 is None or item2 is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # Here we have to use the raw SQL queries, see https://github.com/pgvector/pgvector
    # Notably, we have to convert the vector to a string to comply with the pgvector API
    item2_vector = str(item2.vector.tolist())
    similarity_score = db.execute(
        text(
            "SELECT 1 - (vector <=> :item2_vector) FROM items WHERE id = :item1_id",
        ),
        {"item2_vector": item2_vector, "item1_id": item1.id},
    ).scalar()
    return {"similarity_score": similarity_score}


def get_nearest_neighbors(
    item_id: str,
    nearest_neighbors_count: int,
    db: Session = Depends(get_db),
) -> dict:
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # Here we follow the docs from the pgvector python extension https://github.com/pgvector/pgvector-python
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

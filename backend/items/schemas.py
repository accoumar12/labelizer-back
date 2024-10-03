from __future__ import annotations

from pydantic import BaseModel


class Item(BaseModel):
    id: str
    length: float
    dataset: str
    # vector: list[float]

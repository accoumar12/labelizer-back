from __future__ import annotations

import io

import pandas as pd
from sqlalchemy.orm import Session
from src.triplets import crud


def get_triplets_csv_stream(db: Session) -> io.BytesIO:
    data = crud.get_labeled_triplets(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_csv(stream, index=False)
    stream.seek(0)
    return stream


def get_validation_triplets_csv_stream(db: Session) -> io.BytesIO:
    data = crud.get_validation_labeled_triplets(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_csv(stream, index=False)
    stream.seek(0)
    return stream

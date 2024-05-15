from __future__ import annotations

import io
import shutil
import tempfile
from turtle import up
import zipfile
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from labelizer import crud
from labelizer.app_config import AppConfig

app_config = AppConfig()


def get_db_excel_export(db: Session) -> io.BytesIO:
    data = crud.get_all_data(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_excel(stream, index=False)
    stream.seek(0)
    return stream


def extract_zip(file: UploadFile) -> Path:
    tmp_path = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(file.file, "r") as zip_ref:
        zip_ref.extractall(tmp_path)
    return tmp_path


def check_structure_consistency(
    path_to_be_present: Path,
    path_to_be_removed: Path,
    detail: str,
) -> None:
    if not path_to_be_present.exists():
        shutil.rmtree(path_to_be_removed)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def load_triplets(triplets_path: Path) -> tuple[pd.DataFrame, set[str]]:
    triplets = pd.read_csv(triplets_path)
    triplets_ids = (
        triplets[["reference_id", "left_id", "right_id"]].to_numpy().flatten()
    )
    return triplets, set(triplets_ids)


def get_uploaded_images_ids(uploaded_images_path: Path) -> set[str]:
    uploaded_images = set(uploaded_images_path.iterdir())
    return {file.name.split(".")[0] for file in uploaded_images}


def get_all_images_ids(uploaded_images_ids: set[str]) -> set[str]:
    return {
        file.name.split(".")[0] for file in app_config.images_path.iterdir()
    } | uploaded_images_ids


def update_database(
    db: Session,
    triplets: pd.DataFrame,
    uploaded_images_path: Path,
) -> None:
    crud.create_labelized_triplets(db, triplets)
    uploaded_images = uploaded_images_path.iterdir()
    for file in uploaded_images:
        shutil.move(
            file,
            app_config.images_path / file.name,
        )

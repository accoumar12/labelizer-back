from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from labelizer import crud
from labelizer.app_config import get_app_config

app_config = get_app_config()


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


# TODO: implement a check linked with the canonical images
def get_uploaded_images_ids(uploaded_images_path: Path) -> set[str]:
    uploaded_images = set(uploaded_images_path.iterdir())
    return {
        file.name.split(".")[0]
        for file in uploaded_images
        if not file.name.endswith("_canonical")
    }


def get_all_images_ids(uploaded_images_ids: set[str]) -> set[str]:
    # We use lazy evaluation to avoid checking the content of the images folder if it does not exist
    if not app_config.images_path.exists() or not any(app_config.images_path.iterdir()):
        return uploaded_images_ids
    return {
        file.name.split(".")[0]
        for file in app_config.images_path.iterdir()
        if not file.name.endswith("_canonical")
    } | uploaded_images_ids


def update_database(
    db: Session,
    triplets: pd.DataFrame,
    uploaded_images_path: Path,
) -> None:
    crud.create_labelized_triplets(db, triplets)
    uploaded_images = uploaded_images_path.iterdir()
    for file in uploaded_images:
        destination = app_config.images_path / file.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(file, destination)

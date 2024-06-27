from __future__ import annotations

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import HTTPException, status

from backend.config.config import config

if TYPE_CHECKING:
    import io

logger = logging.getLogger()


def check_structure_consistency(
    path_to_be_present: Path,
    path_to_be_removed: Path,
    detail: str,
) -> None:
    if not path_to_be_present.exists():
        shutil.rmtree(path_to_be_removed)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def get_uploaded_images_ids(uploaded_images_path: Path) -> set[str]:
    uploaded_images = set(uploaded_images_path.iterdir())
    image_ids = {
        file.name.split(".")[0]
        for file in uploaded_images
        if not file.name.split(".")[0].endswith("_canonical")
    }
    canonical_image_ids = {
        file.name.split("_canonical")[0]
        for file in uploaded_images
        if file.name.split(".")[0].endswith("_canonical")
    }
    if image_ids != canonical_image_ids:
        # We have to use this method because we do not know which set is missing elements
        missing_canonicals = image_ids.symmetric_difference(canonical_image_ids)
        msg = f"Discrepancy between images and canonical images: {', '.join(missing_canonicals)}"
        raise ValueError(msg)
    return image_ids


def get_all_images_ids(uploaded_images_ids: set[str]) -> set[str]:
    # We use lazy evaluation to avoid checking the content of the images folder if it does not exist, then checking if it not empty to then iterate over it
    if not config.images_path.exists() or not any(config.images_path.iterdir()):
        return uploaded_images_ids
    return {
        file.name.split(".")[0]
        for file in config.images_path.iterdir()
        if not file.name.endswith("_canonical")
    } | uploaded_images_ids


def extract_zip(file_in_memory: io.BytesIO) -> Path:
    tmp_path = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(file_in_memory, "r") as zip_ref:
        zip_ref.extractall(tmp_path)
    return tmp_path

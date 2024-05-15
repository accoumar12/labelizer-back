import os
from pathlib import Path

_CONFIG = None


class AppConfig:
    def __init__(self) -> None:
        workspace_folder = Path(os.environ["ROOT_PATH"])
        self.images_path = workspace_folder / "data" / "images"
        self.canonical_images_path = workspace_folder / "data" / "canonical_images"
        self.db_path = workspace_folder / "database.db"
        self.dev_mod = bool(os.environ.get("DEV_MOD", False))


def get_app_config() -> AppConfig:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = AppConfig()
    return _CONFIG

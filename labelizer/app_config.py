import os
from pathlib import Path


class AppConfig:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        workspace_folder = Path(os.environ["ROOT_PATH"])
        self.dev_mod = bool(os.environ.get("DEV_MOD", False))
        self.images_path = workspace_folder / "data" / "images"
        self.lock_timeout_in_seconds = 30
        self.vector_dimension = 1280

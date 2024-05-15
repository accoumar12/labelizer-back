import os
from pathlib import Path


class AppConfig:
    _instance = None

    def __init__(self) -> None:
        if AppConfig._instance is not None:
            msg = "this class is a singleton!"
            raise RuntimeError(msg)
        workspace_folder = Path(os.environ["ROOT_PATH"])
        self.images_path = workspace_folder / "images"
        self.db_path = workspace_folder / "database.db"
        self.dev_mod = bool(os.environ.get("DEV_MOD", False))
        AppConfig._instance = self

    @classmethod
    def get_instance(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

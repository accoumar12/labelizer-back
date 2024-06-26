from enum import StrEnum

from pydantic import BaseModel

DEFAULT_UID = "default-user"
DEFAULT_GROUPS = ""


class UserGroup(StrEnum):
    ADMIN = "admin"
    STANDARD = "standard"


class User(BaseModel):
    uid: str
    groups: list[UserGroup]

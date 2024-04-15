from pydantic import BaseModel

DEFAULT_UID = "default-user"
DEFAULT_GROUPS = ""


class UserGroups(StrEnum):
    ADMIN = "admin"


class User(BaseModel):
    uid: str
    groups: list[UserGroups]

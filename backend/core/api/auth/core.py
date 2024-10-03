from logging import getLogger
from typing import Annotated

from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from backend.core.api.auth.models import User, UserGroup

logger = getLogger(__name__)


async def get_current_user(request: Request) -> User:
    """Read user provided in OAuth2 Proxy headers."""
    try:
        #!!! hardcoded values for testing
        uid = "test-user"
        groups = [UserGroup.ADMIN]
        return User(uid=uid, groups=groups)
    except Exception as e:
        logger.exception("An error occurred")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        ) from e


UserSession = Annotated[User, Depends(get_current_user)]


async def get_admin_user(request: Request) -> User:
    """Read user provided in OAuth2 Proxy headers."""
    try:
        user = await get_current_user(request)
        if UserGroup.ADMIN not in user.groups:
            raise ValueError("User is not an admin.")
    except Exception as e:
        logger.exception("An error occurred")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated as an admin user.",
        ) from e
    else:
        return user


AdminUserSession = Annotated[User, Depends(get_admin_user)]

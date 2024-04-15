from logging import getLogger
from typing import Annotated

from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from labelizer.core.api.auth.models import User, UserGroup

logger = getLogger(__file__)


async def get_current_user(request: Request) -> User:
    """Read user provided in OAuth2 Proxy headers"""
    try:
        # uid = request.headers["x-forwarded-email"]
        # groups = request.headers.get("x-forwarded-groups", "")
        #!!! hardcoded values for testing
        uid = "test-user"
        groups = [UserGroup.ADMIN]
        return User(uid=uid, groups=groups)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )


UserSession = Annotated[User, Depends(get_current_user)]


async def get_admin_user(request: Request) -> User:
    """Read user provided in OAuth2 Proxy headers"""
    try:
        user = await get_current_user(request)
        if UserGroup.ADMIN not in user.groups:
            raise ValueError("User is not an admin.")
        return user
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authorized as an admin user.",
        )


AdminUserSession = Annotated[User, Depends(get_admin_user)]

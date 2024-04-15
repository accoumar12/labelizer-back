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
        uid = request.headers["x-forwarded-email"]
        groups = request.headers.get("x-forwarded-groups", "")
        return User(uid=uid, groups=groups)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


UserSession = Annotated[User, Depends(get_current_user)]


async def get_admin_user(request: Request) -> User:
    """Read user provided in OAuth2 Proxy headers"""
    try:
        user = get_current_user(request)
        if UserGroup.ADMIN not in user.groups:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authorized",
            )
        return user
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


AdminUserSession = Annotated[User, Depends(get_admin_user)]

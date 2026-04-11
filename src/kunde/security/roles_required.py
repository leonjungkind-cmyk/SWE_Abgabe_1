"""Überprüfung der erforderlichen Rollen."""

from typing import TYPE_CHECKING, Annotated, Final

from fastapi import Depends, HTTPException, Request, status
from loguru import logger

from kunde.security.dependencies import get_token_service
from kunde.security.role import Role
from kunde.security.token_service import TokenService

if TYPE_CHECKING:
    from kunde.security.user import User

__all__ = ["RolesRequired"]


class RolesRequired:
    """Überprüfung der erforderlichen Rollen bei dependencies=[Depends()]."""

    def __init__(self, required_roles: list[Role] | Role) -> None:
        """Initialisierung mit den erforderlichen Rollen."""
        self.required_roles = required_roles

    def __call__(
        self,
        request: Request,
        service: Annotated[TokenService, Depends(get_token_service)],
    ) -> None:
        """Überprüfung der Rollen des aktuellen Users."""
        user: Final[User] = service.get_user_from_request(request)
        logger.debug("user={}", user)

        if isinstance(self.required_roles, Role):
            if self.required_roles not in user.roles:
                logger.warning(
                    "{} hat nicht die Rolle {}",
                    user,
                    self.required_roles,
                )
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

            request.state.current_user = user
            logger.debug("OK: user={}", user)
            return

        for role in user.roles:
            if role in self.required_roles:
                request.state.current_user = user
                logger.debug("OK: user={}", user)
                return

        logger.warning("{} hat keine der Rollen {}", user, self.required_roles)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

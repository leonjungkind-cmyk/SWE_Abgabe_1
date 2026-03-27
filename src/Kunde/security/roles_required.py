# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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


# https://www.codementor.io/@mandarvaze/how-to-implement-role-based-access-control-with-fastapi-1b76qbxn0s
class RolesRequired:
    """Überprüfung der erforderlichen Rollen bei dependencies=[Depends()]."""

    def __init__(self, required_roles: list[Role] | Role) -> None:
        """Initialisierung mit den erforderlichen Rollen."""
        self.required_roles = required_roles

    # "Called when the instance is 'called' as a function"
    # callable_obj = MyClass()
    # callable_obj(1, 2, 3)  # jetzt wird __call__ aufgerufen
    # https://docs.python.org/3/reference/datamodel.html#object.__call__
    # https://stackoverflow.com/questions/9663562/what-is-the-difference-between-init-and-call
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
            return  # request

        for role in user.roles:
            if role in self.required_roles:
                request.state.current_user = user
                # FastAPI is expecting a value to be returned from dependencies
                logger.debug("OK: user={}", user)
                return  # request
        logger.warning("{} hat keine der Rollen {}", user, self.required_roles)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

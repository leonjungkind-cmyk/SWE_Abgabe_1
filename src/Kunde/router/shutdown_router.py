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

"""REST-Schnittstelle für Shutdown."""

import os
import signal
from typing import Any, Final

from fastapi import APIRouter, Depends
from loguru import logger

from patient.security.role import Role
from patient.security.roles_required import RolesRequired

__all__ = ["router"]


router: Final = APIRouter(tags=["Admin"])


# "Dependency Injection" durch Depends
@router.post("/shutdown", dependencies=[Depends(RolesRequired(Role.ADMIN))])
def shutdown() -> dict[str, Any]:
    """Der Server wird heruntergefahren."""
    logger.warning("Server shutting down without calling cleanup handlers.")
    # https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c#answer-69812984
    # https://github.com/pallets/werkzeug/issues/1752
    # https://docs.python.org/3/library/os.html#os._exit
    # https://docs.python.org/3/library/sys.html#sys.exit
    # sys.exit(0)  # NOSONAR
    # os._exit(0)
    os.kill(os.getpid(), signal.SIGINT)  # NOSONAR
    return {"message": "Server is shutting down..."}

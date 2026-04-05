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

"""DbPopulateController."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from kunde.config.dev.db_populate import DbPopulateService, get_db_populate_service

__all__ = ["router"]


router: Final = APIRouter()


@router.post("/db_populate", tags=["Dev"])
def populate(
    service: Annotated[DbPopulateService, Depends(get_db_populate_service)],
) -> JSONResponse:
    """Die DB mit Testdaten durch einen POST-Request neu laden.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: JSONResponse
    """
    service.populate()
    return JSONResponse(content={"db_populate": "success"})

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

"""Response-Header für IT-Sicherheit setzen."""

from typing import Final

from fastapi import Response

__all__ = ["set_response_headers"]


ONE_YEAR_IN_SECONDS: Final = 365 * 24 * 60 * 60


def set_response_headers(response: Response) -> Response:
    """Response-Header für IT-Sicherheit setzen.

    :param response: Das Response-Objekt, bei dem Header-Daten ergänzt werden
    :return: Das Response-Objekt mit ergänzten Header-Daten
    :rtype: Response
    """
    # https://flask.palletsprojects.com/en/2.2.x/security
    headers: Final = response.headers
    headers["X-Frame-Options"] = "SAMEORIGIN"
    headers["X-XSS-Protection"] = "1; mode=block"
    headers["X-Content-Type-Options"] = "nosniff"
    headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none'"
    headers["Strict-Transport-Security"] = (
        f"max-age={ONE_YEAR_IN_SECONDS}; includeSubDomains"
    )
    return response

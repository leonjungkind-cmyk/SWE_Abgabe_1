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

"""ProblemDetails gemäß RFC 7807."""

from dataclasses import asdict, dataclass

from fastapi import Response
from fastapi.responses import JSONResponse

__all__ = ["create_problem_details"]

BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
PRECONDITION_FAILED = 412
UNPROCESSABLE_CONTENT = 422
PRECONDITION_REQUIRED = 428


@dataclass(eq=False, slots=True, kw_only=True)
class ProblemDetails:
    """Datenstruktur für ProblemDetails gemäß RFC 7807."""

    title: str
    status_code: int
    detail: dict | str | None


def create_problem_details(
    status_code: int, detail: dict | str | None = None
) -> Response:
    """ProblemDetails gemäß RFC 7807 erstellen."""
    problem_details: ProblemDetails

    match status_code:
        case 400:
            problem_details = ProblemDetails(
                title="Bad Request", status_code=status_code, detail=detail
            )
        case 401:
            problem_details = ProblemDetails(
                title="Unauthorized", status_code=status_code, detail=detail
            )
        case 403:
            problem_details = ProblemDetails(
                title="Forbidden", status_code=status_code, detail=detail
            )
        case 412:
            problem_details = ProblemDetails(
                title="Precondition Failed",
                status_code=status_code,
                detail=detail,
            )
        case 422:
            problem_details = ProblemDetails(
                title="Unprocessable Content",
                status_code=status_code,
                detail=detail,
            )
        case 428:
            problem_details = ProblemDetails(
                title="Precondition Required",
                status_code=status_code,
                detail=detail,
            )
        case _:
            problem_details = ProblemDetails(
                title="Client Error", status_code=status_code, detail=detail
            )

    return JSONResponse(
        status_code=status_code,
        content=asdict(obj=problem_details),
        media_type="application/problem+json",
    )

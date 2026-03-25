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

"""Data class für die Login-Daten."""

from dataclasses import dataclass

__all__ = ["LoginData"]


@dataclass
class LoginData:
    """Data class für die Login-Daten."""

    username: str
    """Benutzername"""
    password: str
    """Passwort"""

    class Config:
        """Beispiel für OpenAPI."""

        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "p",  # NOSONAR
            },
        }

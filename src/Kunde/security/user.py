# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Entity-Klasse für Benutzerdaten."""

from dataclasses import dataclass

from patient.security.role import Role


@dataclass()
class User:
    """Entity-Klasse für Benutzerdaten."""

    username: str
    """Benutzername."""

    email: str
    """Emailadresse."""

    nachname: str
    """Nachname."""

    vorname: str
    """Vorname."""

    roles: list[Role]
    """Rollen als Liste von Enums."""

    password: str | None = None
    """Passwort."""

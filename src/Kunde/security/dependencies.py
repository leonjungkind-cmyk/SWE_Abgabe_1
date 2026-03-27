# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Factory-Funktionen für Dependency Injection."""

from kunde.security.token_service import TokenService
from kunde.security.user_service import UserService

_token_service = TokenService()  # Singleton-Objekt


def get_token_service() -> TokenService:
    """Factory-Funktion für TokenService."""
    return _token_service


_user_service = UserService()  # Singleton-Objekt


def get_user_service() -> UserService:
    """Factory-Funktion für UserService."""
    return _user_service

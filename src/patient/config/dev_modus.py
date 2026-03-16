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

"""Konfiguration für den Entwicklungsmodus."""

from typing import Final

from patient.config.config import app_config

__all__ = ["dev_db_populate", "dev_keycloak_populate"]


_dev_toml: Final = app_config.get("dev", {})

dev_db_populate: Final[bool] = bool(_dev_toml.get("db-populate", False))
"""Flag, ob die DB beim Serverstart neu geladen werden soll."""

dev_keycloak_populate: Final[bool] = bool(_dev_toml.get("keycloak-populate", False))
"""Flag, ob Keycloak beim Serverstart neu geladen werden soll."""

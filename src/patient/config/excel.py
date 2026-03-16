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

"""Konfiguration für Excel."""

from typing import Final

from patient.config.config import app_config

__all__ = ["excel_enabled"]


_excel_toml: Final = app_config.get("excel", {})

excel_enabled: Final[bool] = bool(_excel_toml.get("enabled", False))
"""Flag, ob Excel benutzt werden soll (default: False)."""

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

"""Konfiguration aus der TOML-Datei einlesen."""

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from tomllib import load
from typing import Any, Final

from loguru import logger

__all__ = ["app_config", "resources_path"]


resources_path: Final[str] = "patient.config.resources"

_resources_traversable: Final[Traversable] = files(resources_path)
_config_file: Final[Traversable] = _resources_traversable / "app.toml"
logger.debug("config: _config_file={}", _config_file)


with Path(str(_config_file)).open(mode="rb") as reader:
    app_config: Final[dict[str, Any]] = load(reader)
    logger.debug("config: app_config={}", app_config)

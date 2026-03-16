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

"""Konfiguration für Logging."""

from pathlib import Path
from typing import Final

from loguru import logger

__all__ = ["config_logger"]

LOG_FILE: Final = Path("log") / "app.log"


# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html
# https://realpython.com/python-loguru
def config_logger() -> None:
    """Konfiguration für Logging."""
    logger.add(LOG_FILE, rotation="1 MB")

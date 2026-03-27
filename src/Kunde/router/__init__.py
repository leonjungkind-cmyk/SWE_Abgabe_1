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
"""Modul für die REST-Schnittstelle einschließlich Validierung."""

from collections.abc import Sequence

from kunde.router.health_router import liveness, readiness
from kunde.router.health_router import router as health_router
from kunde.router.kunde_router import get, get_by_id, get_nachnamen, kunde_router
from kunde.router.kunde_write_router import (
    delete_by_id,
    kunde_write_router,
    post,
    put,
)
from kunde.router.shutdown_router import router as shutdown_router
from kunde.router.shutdown_router import shutdown

__all__: Sequence[str] = [
    "delete_by_id",
    "get",
    "get_by_id",
    "get_nachnamen",
    "health_router",
    "liveness",
    "kunde_router",
    "kunde_write_router",
    "post",
    "put",
    "readiness",
    "shutdown",
    "shutdown_router",
]

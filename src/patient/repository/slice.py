# Copyright (C) 2024 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Ausschnitt an gefundenen Daten."""

from dataclasses import dataclass
from typing import TypeVar

__all__ = ["Slice"]


T = TypeVar("T")


@dataclass(eq=False, slots=True, kw_only=True)
class Slice[T]:
    """Data class für den Ausschnitt an gefundenen Daten."""

    content: tuple[T, ...]
    """Ausschnitt der gefundenen Datensätze als Tupel beliebiger Länge."""

    total_elements: int
    """Gesamte Anzahl an Datensätzen."""

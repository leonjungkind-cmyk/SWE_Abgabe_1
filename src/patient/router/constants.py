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

"""PatientGetRouter."""

from typing import Final

__all__ = [
    "ETAG",
    "IF_MATCH",
    "IF_MATCH_MIN_LEN",
    "IF_NONE_MATCH",
    "IF_NONE_MATCH_MIN_LEN",
]

ETAG: Final = "ETag"
IF_MATCH: Final = "if-match"
IF_MATCH_MIN_LEN: Final = 3
IF_NONE_MATCH: Final = "if-none-match"
IF_NONE_MATCH_MIN_LEN: Final = 3

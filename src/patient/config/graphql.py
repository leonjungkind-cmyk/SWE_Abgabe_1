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

"""Konfiguration für GraphQL."""

from typing import Final

from strawberry.http.ides import GraphQL_IDE

from patient.config.config import app_config

__all__ = ["graphql_ide"]


_graphql_toml: Final = app_config.get("graphql", {})
_graphiql_enabled: Final = bool(_graphql_toml.get("graphiql-enabled", False))

graphql_ide: Final[GraphQL_IDE | None] = "graphiql" if _graphiql_enabled else None
"""String 'graphiql', falls GraphiQL aktiviert ist, sonst None."""

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

"""Schema für GraphQL durch Strawberry.

Alternative: https://github.com/graphql-python/graphene.
"""

from collections.abc import Sequence
from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from kunde.config.graphql import graphql_ide
from kunde.graphql_api.graphql_types import (
    CreatePayload,
    LoginResult,
    KundeInput,
    Suchparameter,
)
from kunde.repository import Pageable, KundeRepository
from kunde.router.kunde_model import KundeModel
from kunde.security import Role, TokenService, UserService
from kunde.service import (
    NotFoundError,
    KundeDTO,
    KundeService,
    KundeWriteService,
)

__all__ = ["graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

# type kunde {
#     nachname: String!
# }
# input Suchparameter {...}
# type Query {
#     kunde(kunde_id: ID!): kunde!
#     kundeen(suchparameter: Suchparameter): list[kunde!]!
# }


_repo: Final = KundeRepository()
_service: KundeService = KundeService(repo=_repo)
_user_service: UserService = UserService()
_write_service: KundeWriteService = KundeWriteService(
    repo=_repo, user_service=_user_service
)
_token_service: Final = TokenService()


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Kundeendaten zu lesen."""

    @strawberry.field
    def kunde(self, kunde_id: strawberry.ID, info: Info) -> KundeDTO | None:
        """Daten zu einem Kundeen lesen.

        :param kunde_id: ID des gesuchten Kundeen
        :return: Gesuchter kunde
        :rtype: kunde
        :raises NotFoundError: Falls kein kunde gefunden wurde, wird zu GraphQLError
        """
        logger.debug("kunde_id={}", kunde_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            kunde_dto: Final = _service.find_by_id(
                kunde_id=int(kunde_id),
                user=user,
            )
        except NotFoundError:
            return None
        logger.debug("{}", kunde_dto)
        return kunde_dto

    @strawberry.field
    def kundeen(
        self, suchparameter: Suchparameter, info: Info
    ) -> Sequence[KundeDTO]:
        """Kundeen anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen Kundeen
        :rtype: list[kunde]
        :raises NotFoundError: Falls kein kunde gefunden wurde, wird zu GraphQLError
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        # suchparameter: input type -> Dictionary
        # https://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        suchparameter_dict: Final[dict[str, str]] = dict(vars(suchparameter))
        # nicht-gesetzte Suchparameter aus dem Dictionary entfernen
        # Dict Comprehension ab Python 2.7 (2001) https://peps.python.org/pep-0274
        suchparameter_filtered = {
            key: value
            for key, value in suchparameter_dict.items()
            # leerer String "" ist falsy
            if value is not None and value
        }
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            kundeen_dto: Final = _service.find(
                suchparameter=suchparameter_filtered, pageable=pageable
            )
        except NotFoundError:
            return []
        logger.debug("{}", kundeen_dto)
        return kundeen_dto.content


@strawberry.type
class Mutation:
    """Mutations, um Kundeendaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, kunde_input: KundeInput) -> CreatePayload:
        """Einen neuen Kundeen anlegen.

        :param kunde_input: Daten des neuen Kundeen
        :return: ID des neuen Kundeen
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug("kunde_input={}", kunde_input)

        kunde_dict = kunde_input.__dict__
        kunde_dict["adresse"] = kunde_input.adresse.__dict__
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        kunde_dict["rechnungen"] = [
            rechnung.__dict__ for rechnung in kunde_input.rechnungen
        ]

        # Dictonary mit Pydantic validieren
        kunde_model: Final = KundeModel.model_validate(kunde_dict)

        kunde_dto: Final = _write_service.create(kunde=kunde_model.to_kunde())
        payload: Final = CreatePayload(id=kunde_dto.id)  # pyright: ignore[reportArgumentType ]

        logger.debug("{}", payload)
        return payload

    # Mutation, weil evtl. der Login-Zeitpunkt gespeichert wird
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(query=Query, mutation=Mutation)


Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema, context_getter=get_context, graphql_ide=graphql_ide
)

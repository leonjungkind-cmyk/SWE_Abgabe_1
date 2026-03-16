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

from patient.config.graphql import graphql_ide
from patient.graphql_api.graphql_types import (
    CreatePayload,
    LoginResult,
    PatientInput,
    Suchparameter,
)
from patient.repository import Pageable, PatientRepository
from patient.router.patient_model import PatientModel
from patient.security import Role, TokenService, UserService
from patient.service import (
    NotFoundError,
    PatientDTO,
    PatientService,
    PatientWriteService,
)

__all__ = ["graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

# type Patient {
#     nachname: String!
# }
# input Suchparameter {...}
# type Query {
#     patient(patient_id: ID!): Patient!
#     patienten(suchparameter: Suchparameter): list[Patient!]!
# }


_repo: Final = PatientRepository()
_service: PatientService = PatientService(repo=_repo)
_user_service: UserService = UserService()
_write_service: PatientWriteService = PatientWriteService(
    repo=_repo, user_service=_user_service
)
_token_service: Final = TokenService()


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Patientendaten zu lesen."""

    @strawberry.field
    def patient(self, patient_id: strawberry.ID, info: Info) -> PatientDTO | None:
        """Daten zu einem Patienten lesen.

        :param patient_id: ID des gesuchten Patienten
        :return: Gesuchter Patient
        :rtype: Patient
        :raises NotFoundError: Falls kein Patient gefunden wurde, wird zu GraphQLError
        """
        logger.debug("patient_id={}", patient_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            patient_dto: Final = _service.find_by_id(
                patient_id=int(patient_id),
                user=user,
            )
        except NotFoundError:
            return None
        logger.debug("{}", patient_dto)
        return patient_dto

    @strawberry.field
    def patienten(
        self, suchparameter: Suchparameter, info: Info
    ) -> Sequence[PatientDTO]:
        """Patienten anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen Patienten
        :rtype: list[Patient]
        :raises NotFoundError: Falls kein Patient gefunden wurde, wird zu GraphQLError
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
            patienten_dto: Final = _service.find(
                suchparameter=suchparameter_filtered, pageable=pageable
            )
        except NotFoundError:
            return []
        logger.debug("{}", patienten_dto)
        return patienten_dto.content


@strawberry.type
class Mutation:
    """Mutations, um Patientendaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, patient_input: PatientInput) -> CreatePayload:
        """Einen neuen Patienten anlegen.

        :param patient_input: Daten des neuen Patienten
        :return: ID des neuen Patienten
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug("patient_input={}", patient_input)

        patient_dict = patient_input.__dict__
        patient_dict["adresse"] = patient_input.adresse.__dict__
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        patient_dict["rechnungen"] = [
            rechnung.__dict__ for rechnung in patient_input.rechnungen
        ]

        # Dictonary mit Pydantic validieren
        patient_model: Final = PatientModel.model_validate(patient_dict)

        patient_dto: Final = _write_service.create(patient=patient_model.to_patient())
        payload: Final = CreatePayload(id=patient_dto.id)  # pyright: ignore[reportArgumentType ]

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

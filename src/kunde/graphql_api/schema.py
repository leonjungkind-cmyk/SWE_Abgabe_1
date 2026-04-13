"""GraphQL-Schnittstelle der Kundenverwaltung, aufgebaut mit Strawberry.

Alternativ wäre https://github.com/graphql-python/graphene möglich.
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
    AdresseType,
    BestellungType,
    CreatePayload,
    KundeInput,
    KundeType,
    Suchparameter,
)
from kunde.repository import KundeRepository, Pageable
from kunde.router.kunde_model import KundeModel
from kunde.security import TokenService
from kunde.service import KundeReadService, KundeWriteService
from kunde.service.exceptions import NotFoundError

__all__ = ["graphql_router"]


_repo: Final = KundeRepository()
_read_service: Final = KundeReadService(repo=_repo)
_write_service: Final = KundeWriteService(repo=_repo)
_token_service: Final = TokenService()


def _to_kunde_type(dto) -> KundeType:
    return KundeType(
        id=dto.id,
        nachname=dto.nachname,
        email=dto.email,
        version=dto.version,
        adresse=AdresseType(
            plz=dto.adresse.plz,
            ort=dto.adresse.ort,
        ),
        bestellungen=[
            BestellungType(produktname=b.produktname, menge=b.menge)
            for b in dto.bestellungen
        ],
    )


@strawberry.type
class Query:
    """Leseoperationen für die GraphQL-Schnittstelle der Kundenverwaltung."""

    @strawberry.field
    def kunde(self, kunde_id: strawberry.ID, info: Info) -> KundeType | None:
        """Einen einzelnen Kunden anhand seiner ID laden.

        :param kunde_id: Primärschlüssel des gewünschten Kunden
        :param info: Strawberry-Kontext mit FastAPI-Request
        :return: Kundendatensatz oder None, falls kein Treffer
        :rtype: KundeType | None
        """
        logger.debug("kunde_id={}", kunde_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)

        if user is None:
            return None

        try:
            kunde_dto = _read_service.find_by_id(
                kunde_id=int(kunde_id),
                user=user,
            )
        except NotFoundError:
            return None

        logger.debug("{}", kunde_dto)
        return _to_kunde_type(kunde_dto)

    @strawberry.field
    def kunden(
        self,
        suchparameter: Suchparameter,
        info: Info,
    ) -> Sequence[KundeType]:
        """Mehrere Kunden über Filterkriterien ermitteln.

        :param suchparameter: Filterfelder wie nachname oder email
        :param info: Strawberry-Kontext mit FastAPI-Request
        :return: Alle Kunden, die den Kriterien entsprechen
        :rtype: Sequence[KundeType]
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)

        if user is None:
            return []

        suchparameter_dict: Final[dict[str, str]] = dict(vars(suchparameter))
        suchparameter_filtered = {
            key: value
            for key, value in suchparameter_dict.items()
            if value is not None and value
        }
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            kunden_slice = _read_service.find(
                suchparameter=suchparameter_filtered,
                pageable=pageable,
            )
        except NotFoundError:
            return []

        logger.debug("{}", kunden_slice)
        return [_to_kunde_type(dto) for dto in kunden_slice.content]


@strawberry.type
class Mutation:
    """Schreiboperationen für die GraphQL-Schnittstelle der Kundenverwaltung."""

    @strawberry.mutation
    def create(self, kunde_input: KundeInput) -> CreatePayload:
        """Neuen Kunden in der Datenbank persistieren.

        :param kunde_input: Eingabedaten des anzulegenden Kunden
        :return: Enthält die vergebene ID des neuen Kunden
        :rtype: CreatePayload
        :raises EmailExistsError:
            Wenn die Emailadresse bereits einem anderen Kunden gehört
        """
        logger.debug("kunde_input={}", kunde_input)

        kunde_dict = kunde_input.__dict__
        kunde_dict["adresse"] = kunde_input.adresse.__dict__

        kunde_model: Final = KundeModel.model_validate(kunde_dict)
        kunde_dto: Final = _write_service.create(kunde=kunde_model.to_kunde())
        payload: Final = CreatePayload(id=kunde_dto.id)  # pyright: ignore[reportArgumentType]

        logger.debug("{}", payload)
        return payload


schema: Final = strawberry.Schema(query=Query, mutation=Mutation)


Context = dict[str, Request]


def get_context(request: Request) -> Context:
    return {"request": request}


graphql_router: Final = GraphQLRouter[Context](
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)

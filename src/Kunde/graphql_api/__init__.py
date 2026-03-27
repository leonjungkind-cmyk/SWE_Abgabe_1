"""Modul für die GraphQL-Schnittstelle."""

from kunde.graphql_api.graphql_types import (
    AdresseInput,
    CreatePayload,
    KundeInput,
    RechnungInput,
    Suchparameter,
)
from kunde.graphql_api.schema import Mutation, Query, graphql_router

__all__ = [
    "AdresseInput",
    "CreatePayload",
    "Mutation",
    "KundeInput",
    "Query",
    "RechnungInput",
    "Suchparameter",
    "graphql_router",
]

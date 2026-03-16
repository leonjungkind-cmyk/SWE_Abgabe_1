"""Modul für die GraphQL-Schnittstelle."""

from patient.graphql_api.graphql_types import (
    AdresseInput,
    CreatePayload,
    PatientInput,
    RechnungInput,
    Suchparameter,
)
from patient.graphql_api.schema import Mutation, Query, graphql_router

__all__ = [
    "AdresseInput",
    "CreatePayload",
    "Mutation",
    "PatientInput",
    "Query",
    "RechnungInput",
    "Suchparameter",
    "graphql_router",
]

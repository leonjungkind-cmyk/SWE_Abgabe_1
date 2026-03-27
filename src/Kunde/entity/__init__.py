"""Modul für persistente kundendaten."""

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung
from kunde.entity.kunde import Kunde

__all__ = [
    "Adresse",
    "Base",
    "Bestellung",
    "Kunde",
]

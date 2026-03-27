"""Modul für persistente Kundeendaten."""

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.facharzt import Facharzt
from kunde.entity.familienstand import Familienstand
from kunde.entity.geschlecht import Geschlecht
from kunde.entity.kunde import kunde
from kunde.entity.rechnung import Rechnung

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "Adresse",
    "Base",
    "Facharzt",
    "Familienstand",
    "Geschlecht",
    "kunde",
    "Rechnung",
]

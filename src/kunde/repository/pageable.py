"""Steuerungsparameter für paginierte Datenbankabfragen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

__all__ = ["MAX_PAGE_SIZE", "Pageable"]


DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_NUMBER = 0


@dataclass(eq=False, slots=True, kw_only=True)
class Pageable:
    """Enthält Seitengröße und Seitennummer für paginierte Abfragen."""

    size: int
    """Wie viele Einträge eine Seite enthält."""

    number: int
    """Index der aktuellen Seite, beginnend bei 0."""

    @staticmethod
    def create(number: str | None = None, size: str | None = None) -> Pageable:
        """Erzeugt eine Pageable-Instanz aus rohen Query-Parameter-Strings.

        :param number: Gewünschte Seitennummer als String aus dem Query-Parameter.
        :param size: Gewünschte Seitengröße als String aus dem Query-Parameter.
        :return: Fertig initialisiertes Pageable mit validierten Werten.
        :rtype: Pageable
        """
        number_int: Final = (
            DEFAULT_PAGE_NUMBER
            if number is None or not number.isdigit()
            else int(number)
        )
        size_int: Final = (
            DEFAULT_PAGE_SIZE
            if size is None
            or not size.isdigit()
            or int(size) > MAX_PAGE_SIZE
            or int(size) < 0
            else int(size)
        )
        return Pageable(size=size_int, number=number_int)

    @property
    def offset(self) -> int:
        """Berechnet den SQL-Offset anhand von Seitennummer und Seitengröße."""
        return self.number * self.size

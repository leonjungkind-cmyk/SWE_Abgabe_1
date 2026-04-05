"""Paginiertes Ergebnis einer Datenbankabfrage."""

from dataclasses import dataclass

__all__ = ["Slice"]


@dataclass(eq=False, slots=True, kw_only=True)
class Slice[T]:
    """Enthält eine Seite Treffer sowie die Gesamtzahl aller passenden Datensätze."""

    content: tuple[T, ...]
    """Die Treffer der aktuellen Seite als unveränderliches Tupel."""

    total_elements: int
    """Anzahl aller Treffer über alle Seiten hinweg."""

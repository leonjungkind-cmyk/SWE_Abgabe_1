"""Page als Ergebnis einer paginierten REST-Antwort."""

from dataclasses import dataclass
from typing import Any, Final

from kunde.repository.pageable import Pageable

__all__ = ["Page"]


@dataclass
class Page:
    """Repräsentiert eine Seite von Ergebnissen für die REST-Antwort."""

    content: tuple[dict[str, Any], ...]
    page_number: int
    page_size: int
    total_elements: int
    total_pages: int

    @classmethod
    def create(
        cls,
        content: tuple[dict[str, Any], ...],
        pageable: Pageable,
        total_elements: int,
    ) -> "Page":
        """Erzeuge eine Page aus Content und Paginierungsinformationen.

        :param content: Tupel der serialisierten Ergebnisobjekte
        :param pageable: Seitennummer und Seitengröße
        :param total_elements: Gesamtanzahl aller Treffer in der DB
        :return: Page-Instanz
        :rtype: Page
        """
        total_pages: Final = max(
            1, (total_elements + pageable.size - 1) // pageable.size
        )
        return cls(
            content=content,
            page_number=pageable.number,
            page_size=pageable.size,
            total_elements=total_elements,
            total_pages=total_pages,
        )

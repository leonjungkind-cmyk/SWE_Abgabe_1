"""Router für Kunde."""

from collections.abc import Sequence

from kunde.router.kunde_read_router import kunde_read_router
from kunde.router.kunde_write_router import kunde_write_router, post

__all__: Sequence[str] = [
    "kunde_read_router",
    "kunde_write_router",
    "post",
]

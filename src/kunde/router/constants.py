"""Konstanten für HTTP-Header im Router."""

from typing import Final

__all__ = ["ETAG", "IF_NONE_MATCH", "IF_NONE_MATCH_MIN_LEN"]

ETAG: Final = "ETag"
"""Name des ETag-Response-Headers."""

IF_NONE_MATCH: Final = "If-None-Match"
"""Name des If-None-Match-Request-Headers."""

IF_NONE_MATCH_MIN_LEN: Final = 3
"""Mindestlänge eines gültigen ETag-Werts (z.B. '"0"' hat Länge 3)."""

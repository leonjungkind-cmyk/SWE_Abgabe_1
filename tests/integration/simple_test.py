# ruff: noqa: S101, D103
"""Einfache Tests mit pytest (siehe https://awesome-python.com/#testing)."""

from pytest import mark


@mark.simple
def test_simple() -> None:
    # pylint: disable-next=comparison-of-constants, comparison-with-itself
    assert True  # NOSONAR


# https://docs.pytest.org/en/stable/how-to/skipping.html
@mark.skip(reason="Fail")
def test_always_fail() -> None:
    assert not True  # pylint: disable=comparison-of-constants

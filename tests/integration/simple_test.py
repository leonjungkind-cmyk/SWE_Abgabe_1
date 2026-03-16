# ruff: noqa: S101, D103
# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

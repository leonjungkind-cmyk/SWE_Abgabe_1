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

"""DTO-Klasse für die Adresse, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass

import strawberry

from patient.entity import Adresse


# Mit der Funktion asdict() kann ein Objekt einfach in ein dict konvertiert werden
# init=True (default): __init__ fuer die "member variables" wird generiert
# eq=True (default): __eq__ wird generiert
# unsafe_hash=False (default): __hash__ passend zu __eq__ wird generiert
# repr=True (default): __repr__ wird generiert
# frozen=False (default): mutable
# kw_only=False (default): Initialisierungs-Fkt auch ohne "Keyword Arguments" aufrufen
# slots=False (default): __dict__ zur Speicherung statt slots
# slots: schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type
class AdresseDTO:
    """DTO-Klasse für die Adresse, insbesondere ohne Decorators für SQLAlchemy."""

    plz: str
    ort: str

    def __init__(self, adresse: Adresse) -> None:
        """Initialisierung von AdresseDTO durch ein Entity-Objekt von Adresse.

        :param adresse: Adresse-Objekt mit Decorators für SQLAlchemy
        """
        self.plz = adresse.plz
        self.ort = adresse.ort

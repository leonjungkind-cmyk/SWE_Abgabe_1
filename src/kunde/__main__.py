# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""CLI für das Projekt, damit das Modul als Python-Skript ausgeführt werden kann.

Der Aufruf `python -m kunde` ist dadurch möglich, falls folgende Voraussetzungen
erfüllt sind:
- Die virtuelle Umgebung für _venv_ ist aktiviert
- `sys.path` enthält das Verzeichnis `src` (ggf. die Umgebungsvariable `PYTHONPATH` auf
  `src` setzen)
Diese Möglichkeit sollte in einem Docker-Image genutzt werden, so dass der Package
Manager _uv_ zur Laufzeit nicht benötigt wird und deshalb das Image klein gehalten
werden kann.
"""

from kunde.asgi_server import run

__all__ = ["run"]

if __name__ == "__main__":
    run()

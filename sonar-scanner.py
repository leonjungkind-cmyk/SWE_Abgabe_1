# Copyright (C) 2022 - present, Juergen Zimmermann, Hochschule Karlsruhe
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

# Aufruf:   python sonar-scanner.py

"""Python-Script, um den Scanner für SonarQube aufzurufen."""

import subprocess  # noqa: S404
from pathlib import Path
from sysconfig import get_platform

betriebssystem = get_platform()
base_path = (
    (Path("C:\\") / "Zimmermann")
    if betriebssystem in {"win-amd64", "win-arm64", "win32"}
    else Path("Zimmermann")
)
script = Path(base_path) / "sonar-scanner" / "bin" / "sonar-scanner"

subprocess.run(f"{script} -X", shell=True)  # noqa: PLW1510, S602

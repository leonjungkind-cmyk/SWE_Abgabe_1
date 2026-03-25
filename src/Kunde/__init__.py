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

r"""Modul-Deklaration für das Projekt als oberster Namensraum bei Imports.

Das Basis-Verzeichnis `patient` (direkt unter `src`) wird durch `__init__.py` als Modul
für das Projekt deklariert, damit `patient` als oberster Namensraum bei den Imports
verwendet werden kann.

Außerdem kann mit dem Package Manager _uv_ das Modul als Skript aufgerufen werden:
`uv run patient`. Siehe `project.scripts` in `pyproject.toml`.

Desweiteren wird für _uvicorn_ die 'Package-Level' Variable `app` initialisiert.
Dann lautet der Aufruf:

```powershell
uv run uvicorn src.patient:app --ssl-certfile=src\patient\config\resources\tls\certificate.crt --ssl-keyfile=src\patient\config\resources\tls\key.pem
```

Alternativ kann auch die virtuelle Umgebung für _venv_ aktiviert werden und uvicorn
direkt aufgerufen werden:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn src.patient:app --ssl-certfile=src\patient\config\resources\tls\certificate.crt --ssl-keyfile=src\patient\config\resources\tls\key.pem
```

Eine weitere Alternative ist das CLI von FastAPI, das intern _uvicorn_ mit Port _8000_
aufruft - aber _ohne TLS_. Mit dem CLI von FastAPI hat man beim Entwickeln u.a. den
Vorteil, dass ein _Watch-Modus_ im Hinblick auf Dateiänderungen untersützt wird:

```powershell
uv run fastapi dev src\patient
```
"""  # noqa: E501

from patient.asgi_server import run
from patient.fastapi_app import app

__all__ = ["app", "main"]


def main():  # noqa: RUF067
    """main-Funktion, damit das Modul als Skript aufgerufen werden kann."""
    run()

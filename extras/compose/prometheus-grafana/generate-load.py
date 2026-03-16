# Copyright (C) 2024 - present, Juergen Zimmermann, Hochschule Karlsruhe  # noqa: D100
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

# Aufruf:   python extras/compose/prometheus-grafana/generate-load.py

# urllib statt requests oder httpx, damit das Skript ohne Dependencies läuft

from json import dumps, loads
from pathlib import Path
from ssl import create_default_context
from time import sleep
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# 50 Millisekunden
SLEEP_IN_SECONDS = 0.05

# Wurzelverzeichnis des Projekts
project_root = Path(__file__).resolve().parents[3]
cafile = (
    project_root
    / "src"
    / "patient"
    / "config"
    / "resources"
    / "tls"
    / "certificate.crt"
)
ssl_context = create_default_context(cafile=str(cafile))

token_url = "https://localhost:8000/auth/token"  # noqa: S105
token_dict = {
    "username": "admin",
    "password": "p",
}
token_data = dumps(token_dict).encode("utf-8")
# https://docs.python.org/3/library/urllib.request.html#request-objects
token_request = Request(token_url, data=token_data, method="POST")
with urlopen(token_request, context=ssl_context) as response:  # noqa: S310
    body_text = response.read().decode("utf-8")
    token = loads(body_text)["token"]
    print(f"token={token}")
    print()

index = 1
while index >= 1:
    patient_id: int
    if index % 2 == 0:
        patient_id = 20
    elif index % 3 == 0:
        patient_id = 30
    elif index % 5 == 0:
        patient_id = 40
    elif index % 7 == 0:
        patient_id = 50
    else:
        patient_id = 1
    print(f"id={patient_id}")

    url = f"https://localhost:8000/rest/{patient_id}"
    # https://docs.python.org/3/library/urllib.request.html#request-objects
    request = Request(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="GET",
    )

    # https://docs.python.org/3/library/urllib.request.html
    try:
        response = urlopen(request, context=ssl_context)  # noqa: S310
    except HTTPError as e:
        print(f"Fehler bei id={patient_id}: code={e.code}")
        continue

    sleep(SLEEP_IN_SECONDS)
    index += 1

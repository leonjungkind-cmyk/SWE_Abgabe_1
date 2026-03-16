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

# Aufruf:   uvx locust -f .\tests\lasttest\locustfile.py

#           http://localhost:8089
#           z.B. $env:LOGURU_LEVEL = 'INFO'
#                export LOGURU_LEVEL='INFO'
#           Number of users: 50
#           Ramp Up (users started/second): 5
#           Host: https://localhost:8000

"""Lasttest mit Locust."""

from typing import Final, Literal

import urllib3
from locust import HttpUser, constant_throughput, task

# https://stackoverflow.com/questions/27981545/suppress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho#answer-44615889
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# https://docs.locust.io/en/stable/api.html#httpuser-class
class GetUser(HttpUser):
    """Lasttest für GET-Requests."""

    # https://docs.locust.io/en/stable/writing-a-locustfile.html#wait-time-attribute
    # https://docs.locust.io/en/stable/api.html#locust.User.wait_time
    # https://docs.locust.io/en/stable/api.html#locust.wait_time.constant_throughput
    # 50 "Task Iterations" pro Sekunde
    wait_time = constant_throughput(0.1)
    MIN_USERS: Final = 500
    MAX_USERS: Final = 500

    # https://docs.locust.io/en/stable/writing-a-locustfile.html#on-start-and-on-stop-methods
    def on_start(self) -> None:
        """Start-Skript, um einen JWT im Header für Requests zu speichern."""
        # selbst-signiertes Zertifikat
        self.client.verify = False

        # https://docs.locust.io/en/stable/api.html#httpsession-class
        # https://docs.locust.io/en/stable/api.html#response-class
        # https://requests.readthedocs.io/en/latest/api#requests.Response
        response: Final = self.client.post(
            url="/auth/token", json={"username": "admin", "password": "p"}
        )
        body: Final[dict[Literal["token"], str]] = response.json()
        token: Final = body["token"]
        self.client.headers = {"Authorization": f"Bearer {token}"}

    # https://docs.locust.io/en/stable/api.html#locust.task
    # https://docs.locust.io/en/stable/api.html#locust.User.weight
    @task(100)
    def get_id(self) -> None:
        """GET-Requests mit einer ID als Pfadparameter."""
        for patient_id in [1, 20, 30, 40, 50, 60]:
            response = self.client.get(f"/rest/{patient_id}")
            print(f"{response.json()['id']}")

    @task(200)
    def get_nachname(self) -> None:
        """GET-Requests mit dem Nachnamen als Query-Parameter."""
        for teil in ["a", "i", "n", "e", "v"]:
            self.client.get("/rest", params={"nachname": teil})

    @task(150)
    def get_email(self) -> None:
        """GET-Requests mit der Emailadresse als Query-Parameter."""
        for email in [
            "admin@acme.com",
            "alice@acme.de",
            "alice@acme.edu",
            "alice@acme.ch",
            "diana@acme.uk",
            "eve@acme.jp",
        ]:
            self.client.get("/rest", params={"email": email})

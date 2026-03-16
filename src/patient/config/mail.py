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

"""Konfiguration für Mailserver."""

from typing import Final

from patient.config.config import app_config

__all__ = ["mail_enabled", "mail_host", "mail_port", "mail_timeout"]


_mail_toml: Final = app_config.get("mail", {})

mail_enabled: Final = bool(_mail_toml.get("enabled", True))
"""True, falls der Mailserver aktiviert ist."""

mail_host: Final[str] = _mail_toml.get("host", "mail")
"""Rechnername des Mailservers."""

mail_port: Final[int] = _mail_toml.get("port", 25)
"""Port des Mailservers."""

mail_timeout: Final[float] = _mail_toml.get("timeout", 1.0)
"""Timeout für den Mailserver in Sekunden."""

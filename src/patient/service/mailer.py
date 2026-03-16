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

"""Funktionen für E-Mails."""

# https://docs.python.org/3/library/smtplib.html
from email.mime.text import MIMEText
from email.utils import make_msgid
from smtplib import SMTP, SMTPServerDisconnected
from socket import gaierror
from typing import Final
from uuid import uuid4

from loguru import logger

from patient.config import (
    mail_enabled,
    mail_host,
    mail_port,
    mail_timeout,
)
from patient.service.patient_dto import PatientDTO

__all__ = ["send_mail"]

# WhatsApp-Nachricht durch PyWhatKit: https://github.com/Ankit404butfound/PyWhatKit
# knockknock fuer: SMS, Discord, Slack, Microsoft Teams, Telegram, ...

# Mail-Client konfigurieren
MAILSERVER: Final = mail_host
PORT: Final = mail_port
SENDER: Final = "Python Server <python.server@acme.com>"
RECEIVERS: Final = ["Buchhaltung <buchhaltung@acme.com>"]
TIMEOUT: Final = mail_timeout


def send_mail(patient_dto: PatientDTO) -> None:
    """Funktion, um eine E-Mail zu senden.

    :param patient_dto: Patienten-Daten
    """
    # Alternativen zu smtplib:
    # - Marrow Mailer https://github.com/marrow/mailer
    # - EZGmail https://github.com/asweigart/ezgmail
    logger.debug("{}", patient_dto)
    if not mail_enabled:
        logger.warning("send_mail: Der Mailserver ist deaktiviert")
        return

    # Body und Subject
    msg: Final = MIMEText(f"Neuer Patient: <b>{patient_dto.nachname}</b>")
    msg["Subject"] = f"Neuer Patient: ID={patient_dto.id}"
    # https://docs.python.org/3/library/email.utils.html#email.utils.make_msgid
    msg["Message-ID"] = make_msgid(idstring=str(uuid4()))

    try:
        logger.debug("mailserver={}, port={}", MAILSERVER, PORT)
        # https://docs.python.org/3/library/smtplib.html
        with SMTP(host=MAILSERVER, port=PORT, timeout=TIMEOUT) as smtp:
            # ggf. TLS verwenden und einloggen
            # smtp.starttls()
            # smtp.login("my_username", "my_password")
            smtp.sendmail(from_addr=SENDER, to_addrs=RECEIVERS, msg=msg.as_string())
            logger.debug("msg={}", msg)
    except ConnectionRefusedError:
        # https://docs.python.org/3/library/exceptions.html:
        # ConnectionRefusedError -> ConnectionError -> OSError
        # TODO https://github.com/python/cpython/issues/102414
        logger.warning("ConnectionRefusedError")
    except SMTPServerDisconnected:
        # z.B. bei Timeout
        # https://docs.python.org/3/library/smtplib.html
        # SMTPServerDisconnected -> SMTPException -> OSError
        logger.warning("SMTPServerDisconnected")
    except gaierror:
        # gai = getaddrinfo()  # NOSONAR
        logger.warning("socket.gaierror: Laeuft der Mailserver im virtuellen Netzwerk?")

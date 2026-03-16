# Hinweise zur Konfiguration von Mailpit

<!--
  Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.
-->

[Jürgen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de)

## Named Volume

Die Daten zu den eingegangen Emails werden im _Named Volume_ `mailpit`
abgespeichert, was deshalb zuvor erzeugt werden muss.

```shell
    docker volume create mailpit
```

## Mailpit als Mailserver starten

In einer PowerShell oder Bash wird _Mailpit_ als Docker Container gestartet.
Dabei werden die Daten zu den eingegangen Emails im _Named Volume_ `mailpit`
abgespeichert.

```shell
    cd extras/compose/mailpit
    docker compose up
```
## Netshoot als Mailclient

Zunächst wird in einer 2. PowerShell oder Bash ein Docker Container mit _Netshoot_
gestartet, damit man `telnet` als Netzwerkkommando aufrufen kann:

```shell
    cd extras/compose/debug
    docker compose up
```

In einer 3. PowerShell oder Bash wird mittels `telnet` eine Test-Mail abgeschickt:

```shell
    cd extras/compose/debug
    docker compose exec netshoot bash

    {
    echo "EHLO mailpit"
    echo "MAIL FROM: <sender@acme.com>"
    echo "RCPT TO: <recipient@acme.com>"
    echo "DATA"
    echo "From: The Sender <sender@acme.com>"
    echo "To: The Recipient <recipient@acme.com>"
    echo "Subject: My Subject"
    echo ""
    echo "My message body"
    echo "."
    echo "QUIT"
    } | telnet mailpit 1025
```

## Web-Oberfläche von Mailpit

_Mailpit_ beinhaltet einen Webserver, so dass man in einem Webbrowser überprüfen
kann, ob die zuvor abgeschickte Email auch angekommen ist. Dazu ruft man in einem
Webbrowser die URL `http://localhost:8025` auf.

## Herunterfahren und Beenden

Nun kann man die 3. PowerShell bzw. Bash mit `exit` beenden.

In der 2. PowerShell bzw. Bash im Verzeichnis `extras/compose/debug` fährt man
den Container für _Netshoot_ mit `docker compose down` herunter und beendet den
Mailserver bzw. _Mailpit_, indem man im Verzeichnis `extras/compose/mailpit`
ebenfalls `docker compose down` aufruft.

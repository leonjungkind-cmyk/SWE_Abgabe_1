# Hinweise zur Installation und Konfiguration von PostgreSQL

<!--
  Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe

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

[Juergen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de)

## Start des Servers

Für eine statische Codeanalyse durch _SonarQube_ muss zunächst der
SonarQube-Server mit _Docker Compose_ als Docker-Container gestartet werden:

```shell
    # Windows:
    cd extras\compose\sonarqube
    # macOS/Linux:
    cd extras/compose/sonarqube

    docker compose up
```

## Passwort setzen

Wenn der Server zum ersten Mal gestartet wird, ruft man in einem Webbrowser die
URL `http://localhost:9000` auf. In der Startseite muss man sich einloggen und
verwendet dazu als Loginname `admin` und ebenso als Password `admin`. Danach
wird man weitergeleitet, um das initiale Passwort zu ändern.

## Token generieren

Nun wählt man in der Webseite rechts oben das Profil über _MyAccount_ aus und
klickt auf den Menüpunkt _Security_ links. Im Abschnitt _Generate Tokens_ macht
man nun die folgende Eingaben:

- _Name_: z.B. HKA
- _Type_: _Global Analysis Token_ auswählen
- _Expires in_: z.B. _90 days_ auswählen

Abschließend klickt man auf den Button _Generate_.

## Token für sonar-scanner.mts

Den generierten Token trägt man im Skript `scripts\sonar-scanner.mts` ein.

## Scanner

Nachdem der Server gestartet ist, wird der SonarQube-Scanner in einer zweiten
PowerShell mit `python sonar-scanner.py` gestartet. Das Resultat kann dann in der
Webseite des zuvor gestarteten Servers über die URL `http://localhost:9000`
inspiziert werden. Falls es dabei zu einem Fehler kommt, kann man auch direkt
`C:\Users\<MY__USER>\.sonar\native-sonar-scanner\sonar-scanner-...\bin\sonar-scanner`
aufrufen.

## Herunterfahren des Servers

Abschließend wird der oben gestartete Server heruntergefahren.

```shell
    # Windows:
    cd extras\compose\sonarqube
    # macOS/Linux:
    cd extras/compose/sonarqube

    docker compose down
```

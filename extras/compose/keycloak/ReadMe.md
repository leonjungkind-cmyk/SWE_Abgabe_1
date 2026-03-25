# Hinweise zu Keycloak als "Authorization Server"

<!--
  Copyright (C) 2024 - present Juergen Zimmermann, Hochschule Karlsruhe

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

## Inhalt

- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Client Secret](#client-secret)
- [Ergänzung des eigenen Server-Projekts](#ergänzung-des-eigenen-server-projekts)
- [Bruno mit einem Access Token](#bruno-mit-einem-access-token)
- [Optional: Inspektion der H2-Datenbank von Keycloak](#optional-inspektion-der-h2-datenbank-von-keycloak)
- [Initial Access Token](#initial-access-token)

## Installation

_Keycloak_ wird als Docker Container gestartet werden, wobei die Daten sowie das
Zertifikat und der private Schlüssel in einem _Named Volume_ abgespeichert
werden. Das selbst-signierte Zertifikat ist in der Datei `extras\compose\keycloak\certificate.crt`
und der private Schlüssel in `extras\compose\keycloak\key.pem` bereitgestellt.
Zunächst wird das Named Volume `kc_data` für die künftigen Daten und das Named
Volume `kc_tls` für das Zertifikat und den privaten Schlüssel angelegt:

```shell
    docker volume create kc_data
    docker volume create kc_tls
```

Für Details zu Volumes siehe https://docs.docker.com/engine/storage/volumes.

Mit dem _Hardened Image_ für _Keycloak_ `dhi.io/keycloak` wird ein Container so
gestartet, dass nur eine _Bash_ mit dem Linux-Superuser mit UID `0` und GID `0`
läuft. Es wird lediglich das Dateisystem vom Keycloak-Image einschließlich der
Named Volumes für Kopiervorgänge in die neu angelegten Named Volumes benötigt
sowie die Berechtigung zum Ändern vom Linux-Owner und von der Linux-Group (s.u.).
`dhi` steht übrigens für _Docker Hardened Image_.

```shell
    # Windows
    cd extras\compose\keycloak
    docker run -v kc_tls:/opt/keycloak/tls -v ./tls:/tmp/tls:ro `
      --rm -it -u 0:0 --entrypoint '' dhi.io/keycloak:26.5.5-debian13 /bin/bash

    # macOS/Linux
    cd extras/compose/keycloak
    docker run -v kc_tls:/opt/keycloak/tls -v ./tls:/tmp/tls:ro \
      --rm -it -u 0:0 --entrypoint '' dhi.io/keycloak:26.5.5-debian13 /bin/bash

        mkdir /opt/keycloak/tls
        cp /tmp/tls/* /opt/keycloak/tls
        chown -R nonroot:nonroot /opt/keycloak/tls
        exit
```

Um das Zertifikat und den privaten Schlüssel in das Named Volume `kc_tls` kopieren
zu können, wurde das lokale Verzeichnis `.\tls` in `/tmp/tls` bereitgestellt.
In der _bash_ werden deshalb das Zertifikat und der private Schlüssel aus dem
Verzeichnis `/tmp/tls` nach `/opt/keycloak/tls` und deshalb in das Named Volume
`kc_tls` kopiert. Danach wird der Linux-Owner und die -Gruppe jeweils auf `nonroot`
gesetzt.

Jetzt kann der Container für _Keycloak_ gestartet werden:

```shell
    docker compose up
```

Wenn der Container gestartet ist, läuft er intern mit _HTTP_ und Port `8080` sowie
mit _HTTPS_ und Port `8443`. In einer zweiten Shell kann zunächst überprüft werden,
ob die H2-Datenbank für die Speicherung der Keycloak-Daten angelegt wurde:

```shell
    # Windows
    cd extras\compose\keycloak

    # macOS
    cd extras/compose/keycloak

    docker compose exec keycloak bash -c 'ls -l /opt/keycloak/data/h2/keycloakdb.mv.db'
```

In `compose.yml` sind unterhalb von `environment:` der temporäre Administrator
mit Benutzername und Passwort konfiguriert, und zwar Benutzername `tmp` und
Passwort `p`.

## Konfiguration

Nachdem Keycloak als Container gestartet ist, sind folgende umfangreiche
Konfigurationsschritte _sorgfältig_ durchzuführen, nachdem man in einem
Webbrowser `https://localhost:8843` oder `http://localhost:8880` aufgerufen hat.
Das Mapping von Port `8443` auf `8843` und von `8080` auf `8880` ist in
`compose.yml` eingetragen.

```text
    Username    tmp
    Password    p
        siehe extras\compose\keycloak\compose.yml

    Menüpunkt "Users"
        Button <Add user> anklicken
            Username    admin
            Email       admin@acme.com
            First name  Keycloak
            Last name   Admin
            <Create> anklicken
        Tab "Credentials" anklicken
            Button <Set password> anklicken
                Password                p
                Password confirmation   p
                Temporary               Off
                Button <Save> anklicken
                Button <Save password> anklicken
        Tab "Role mapping" anklicken
            Im Drop-Down-Menü "Assign role" den Eintrag "Realm roles" auswählen
                Checkbox "admin" anklicken
                Button <Assign> anklicken
        Drop-Down-Menü in der rechten oberen Ecke
            "Sign-Out" anklicken

    Einloggen
        Username    admin
        Password    p

    Menüpunkt "Manage realms" anklicken
        Button <Create realm> anklicken
            Realm name      python
            <Create> anklicken

    Menüpunkt "Clients"
        <Create client> anklicken
        Client ID   python-client
        Name        Python Client
        <Next>
            "Capability config"
                Client authentication       On
                Authorization               Off (ist voreingestellt)
                Authentication Flow         Standard flow                   Haken setzen
                                            Direct access grants            Haken setzen
                                            Service account roles           Haken setzen
        <Next>
            Root URL                https://localhost:8443
            Valid redirect URIs     *
            Web origins             +
        <Save>

        python-client
            Tab "Roles"
                <Create Role> anklicken
                Role name       admin
                <Save> anklicken
            Breadcrumb "Client details" anklicken
            Tab "Roles"
                <Create Role> anklicken
                Role name       patient
                <Save> anklicken

    # https://www.keycloak.org/docs/latest/server_admin/index.html#assigning-permissions-using-roles-and-groups
    Menüpunkt "Users"
        <Add user>
            Required User Actions:      Überprüfen, dass nichts ausgewählt ist
            Username                    admin
            Email                       admin@acme.com
            First name                  Python
            Last name                   Admin
            <Create> anklicken
            Tab "Credentials"
                <Set password> anklicken
                    "p" eingeben und wiederholen
                    "Temporary" auf "Off" setzen
                    <Save> anklicken
                    <Save password> anklicken
            Tab "Role Mapping"
                Drop-Down-Menü "Assign role" anklicken und "Client roles" auswählen
                    "admin"         Haken setzen     (ggf. blättern)
                    "manage-users"  Haken setzen
                    "query-users"   Haken setzen
                    "realm-admin"   Haken setzen
                    "view-users"    Haken setzen
                    <Assign> anklicken
            Tab "Details"
                Required user actions       Überprüfen, dass nichts ausgewählt ist
                <Save> anklicken
        Breadcrumb "Users" anklicken
            WICHTIG: "admin" ist mit der Emailadresse aufgelistet

    Menüpunkt "Realm settings"
        Tab "Sessions"
            # Refresh Token: siehe https://stackoverflow.com/questions/52040265/how-to-specify-refresh-tokens-lifespan-in-keycloak
            SSO Session Idle                                1 Hours
            <Save> anklicken
        Tab "Tokens"
            Access Tokens
                Access Token Lifespan                       30 Minutes
                Access Token Lifespan For Implicit Flow     30 Minutes
                <Save> anklicken
```

Mit der URL `https://localhost:8843/realms/python/.well-known/openid-configuration`
kann man in einem Webbrowser die Konfiguration als JSON-Datensatz erhalten.

Die Bestandteile der Basis-URL `https://localhost:8443/realms/python` sind in der
Konfigurationsdatei `src\patient\config\resources\app.toml` in der _Table_ `[keycloak]`
eingetragen:

- `schema`: Defaultwert ist `https`
- `host`: Defaultwert ist `keycloak`
- `port`: Defaultwert ist `8443`

Die Defaultwerte sind in `src\patient\config\keycloak.py` definiert.

## Client Secret

In der Datei `src\patient\config\resources\app.toml` muss man `client-secret` auf
folgenden Wert aus _Keycloak_ setzen:

- Menüpunkt `Clients`
- `python-client` aus der Liste beim voreingestellten Tab `Clients list` auswählen
- Tab `Credentials` anklicken
- Die Zeichenkette beim Label `Client Secret` kopieren.

Diese Zeichenkette wird auch für _Bruno_ und `extras\compose\patient\app.toml`
benötigt.

## Ergänzung des eigenen Server-Projekts

Im Wurzelverzeichnis des Projekts in der Datei `.env` muss man die
Umgebungsvariable `CLIENT_SECRET` auf den Wert vom obigen _Client Secret_ aus
_Keycloak_ setzen und ebenso in `extras\compose\buch\.env`:

In der Klasse `AuthController` ist eine REST-Schnittstelle implementiert, mit
der man durch einen POST-Request mit dem Pfad `/auth/token` einen _Access Token_
und einen _Refresh Token_ direkt vom eigenen Server anfordern kann, falls im
Request-Body ein JSON-Datensatz mit den Properties `username` und `password`
mitgeschickt wird.

## Bruno mit einem Access Token

Siehe `ReadMe.md` in `extras\bruno`.

## Optional: Inspektion der H2-Datenbank von Keycloak

Defaultmäßig verwaltet Keycloak seine Daten in einer _H2_-Datenbank - in einer
Produktivumgebung würde man stattdessen ein DB-System wie z.B. _PostgreSQL_
oder _Oracle_ konfigurieren.

**VORSICHT**:Da H2 ein Single-User DB-System ist, sollte man auf keinen Fall die
H2-Datenbank bei gestartetem Keycloak inspizieren, sondern muss den Keycloak-Server
mit `docker compose down` unbedingt herunterfahren!!!

Die H2-Datenbank liegt in der (Linux-) Datei `/opt/keycloak/data/h2/keycloakdb.mv.db`,
und das Verzeichnis `/opt/keycloak/data` liegt wiederum im _Named Volume_ `kc_data`.
Durch die nachfolgenden Kommandos startet man mit einem _H2_-Image einen Container
und in diesem Container eine `Bash`-Shell, wobei das Named Volume mit der H2-Datenbank
von Keycloak als Volume (`-v`) eingebunden wird. Innerhalb der Bash ist dann das
Java-Archiv (`.jar`) verfügbar, womit das CLI von H2 so gestartet werden kann,
dass man auf die H2-Datenbank aus dem Named Volume zugreifen kann. Innerhalb vom CLI
mit dem Prompt `sql>` kann man dann SQL-Kommandos absetzen, z.B. um sich sämtliche
Tabellen von Keycloak auflisten zu lassen. Abschließend beendet man das zunächst
das CLI und danach die Bash

```shell
    docker run --rm -it -v kc_data:/opt/keycloak/data:ro oscarfonts/h2:2.3.232 bash
        java -cp /opt/h2/bin/h2*.jar org.h2.tools.Shell \
          -url jdbc:h2:file:/opt/keycloak/data/h2/keycloakdb -user "" -password ""
              SHOW TABLES;
              SELECT * FROM USER_ENTITY;
              SELECT * FROM USER_ROLE_MAPPING;
              EXIT
        exit
```

**VORSICHT: AUF KEINEN FALL IRGENDEINE TABELLE EDITIEREN, WEIL MAN SONST
KEYCLOAK NEU AUFSETZEN MUSS!**

## Initial Access Token

Ein _Initial Access Token_ für z.B. einen API-Client wurde bei der obigen Konfiguration
für _Keycloak_ folgendermaßen erzeugt:

- Menüpunkt `Clients`
- Tab `Initial access token` anklicken
- Button `Create` anklicken und eine hinreichend lange Gültigkeitsdauer einstellen.

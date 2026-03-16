# Hinweise zu Bruno

<!--
  Copyright © 2025 - present Juergen Zimmermann, Hochschule Karlsruhe

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
-->

[Juergen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de)

## Inhalt

- [Desktop App für ein selbst-signiertes Zertifikat](#desktop-app-für-ein-selbst-signiertes-zertifikat)
- [Erweiterung für VS Code](#erweiterung-für-vs-code)
  - [Collection öffnen](#collection-öffnen)
  - [Selbst-signiertes Zertifikat](#selbst-signiertes-zertifikat)
- [Sensible Daten](#sensible-daten)
- [Autorisierung mit OAuth 2](#autorisierung-mit-oauth-2)
  - [Password Credentials](#password-credentials)
  - [Authorization Code](#authorization-code)
- [Developer Mode](#developer-mode)

## Desktop App für ein selbst-signiertes Zertifikat

Um auf einen Server mit selbst-signiertem Zertifikat zugreifen zu können,
muss man die _Preferences_ in der linken unteren Ecke anklicken und
im anschließenden Dialog bei _SSL/TLS Certificate Verification_ den
Haken entfernen.

## Erweiterung für VS Code

### Collection öffnen

Zunächst klickt man auf das Bruno-Icon in der linken Seitenleiste. Danach auf
das Plus-Icon oben im Bruno-Fenster (Tooltipp "Collections") und wählt den
Menüpunkt "Open Collection" aus.

### Selbst-signiertes Zertifikat

Um auf einen Server mit selbst-signiertem Zertifikat zugreifen zu können,
muss man zunächst auf das Bruno-Icon in der linken Seitenleiste klicken.
Anschließend klickt man auf das Icon für die Einstellungen (Zahnrad)
oben rechts im Bruno-Fenster (Tooltipp "Open Bruno Settings"). Danach wählt man
in der linken Menüleiste den Punkt _General_ aus und entfernt den Haken bei
_Enable SSL Verification

## Sensible Daten

Sensible Daten, wie z.B. Passwörter oder evtl. auch Benutzernamen, sollte man nicht
als gewöhnliche Variable bei einer Collection, einem Folder oder einem Request
ablegen, da sie sonst evtl. im Klartext in einem Versionsierungssystem wie Git
abgelegt werden würden. Dazu klickt man rechts oben auf das Dropdown-Menü _No environments_
und anschließend auf den Button _+ Create_. Nun gibt man einen Namen, z.B. `python` ein
und klickt auf `Create`. Im nachfolgenden Dialog gibt man dann die Variablennamen
und deren Werte ein. In der Spalte _Secret_ kann man dann einen Haken setzen, so dass
künftig die Werte nicht im Klartext, sondern als Sterne angezeigt werden.
Abschließend darf man nicht vergessen, die Einträge mit dem Button _Save_ abzuspeichern.

_Secrets_ werden folgendermaßen abgespeichert:

| Betriebssystem | Verzeichnis                           |
| -------------- | ------------------------------------- |
| Windows        | `$env:APPDATA\Bruno`                  |
| macOS          | `~/Library/Application Support/Bruno` |
| Linux          | `~/.config/Bruno`                     |

Für das vorliegende Beispiel müssen deshalb für das Environment `kunde` folgende Werte
gesetzt werden:

- `clientSecret`: siehe Kubernetes
- `password`: Administrationspasswort für Kubernetes, z.B. `p`

## Autorisierung mit OAuth 2

Für _OAuth 2_ gibt es u.a. die beiden Möglichkeiten _Password Credentials_ und
_Authorization Code_. Bei _Password Credentials_ werden Benutzername und Passwort
in einem Formular von Bruno eingetragen und sind fortan bei jedem Request, der abgeschickt
wird vorhanden und auch dieselben Werte. Bei _Authorization Code_ wird ein Dialog mit dem
_Authorization Server_ aufgebaut und man gibt die Werte interaktiv ein.

### Password Credentials

Voraussetzung für _Password Credentials_ ist, dass in _Keycloak_ beim entsprechenden
Client bei _Authentication flow_ für _Direct access grants_ der Haken gesetzt ist.
Für OAuth 2 klickt man bei einer Collection, einem Folder oder einem Request zunächst
den Tab _Auth_ an. Im Dropdown-Menü wählt man dann _Password Credentials_ aus und gibt
z.B. folgende Werte ein:

| Option               | Wert                                 |
| -------------------- | ------------------------------------ |
| _Access Token URL_   | `{{oidcTokenUrl}}`                   |
| _Username_           | `{{username}}`                       |
| _Password_           | `{{password}}`                       |
| _Client ID_          | `{{clientId}}`                       |
| _Client Secret_      | `{{clientSecret}}`                   |
| _Add Credentials to_ | _Request Body_ aus dem Dropdown-Menü |
| _Header Prefix_      | `Bearer`                             |

`oidcTokenUrl` könnte eine Variable mit dem Wert `http://localhost:8880/realms/spring/protocol/openid-connect/token`
sein. `clientId` und `clientSecret` könnten aus dem _Environment_ (s.o.) sein
und die Werte für _Client ID_ und _Client Secret_ aus _Keycloak_ enthalten.
Nun klickt man auf den Button _Get Access Token_, so dass der von _Keycloak_
angeforderte Token für nachfolgende Requests verwendet wird.

### Authorization Code

Für OAuth 2 klickt man bei einer Collection, einem Folder oder einem Request zunächst
den Tab _Auth_ an. Im Dropdown-Menü wählt man dann _Authorization Code_ aus und gibt
z.B. folgende Werte ein:

| Option               | Wert                                 |
|:---------------------|:-------------------------------------|
| _Callback URL_       | `{{baseUrl}}`                        |
| _Authorization URL_  | `{{oidcAuthUrl}}`                    |
| _Access Token URL_   | `{{oidcTokenUrl}}`                   |
| _Client ID_          | `{{clientId}}`                       |
| _Client Secret_      | `{{clientSecret}}`                   |
| _Add Credentials to_ | _Request Body_ aus dem Dropdown-Menü |
| _Header Prefix_      | `Bearer`                             |

`baseUrl` könnte eine Collection-Variable mit dem Wert `https://localhost:8443` sein,
`oidcAuthUrl` eine Variable mit `http://localhost:8880/realms/spring/protocol/openid-connect/auth`
für _Keycloak_ und `oidcTokenUrl` eine Variable mit `http://localhost:8880/realms/spring/protocol/openid-connect/token`.
`clientId` und `clientSecret` könnten aus dem _Environment_ (s.o.) sein
und die Werte für _Client ID_ und _Client Secret_ aus _Keycloak_ enthalten.
Nun klickt man auf den Button _Get Access Token_, so dass eine Verbindung
mit _Keycloak_ aufgebaut wird und man im Dialogfenster den Benutzernamen
und das Passwort eingeben kann, wofür man einen Token anfordert. Dieser
Token wird dann für nachfolgende Requests verwendet.

## Developer Mode

Mit _JavaScript_ kann man Requests zu einem Server schicken, um z.B. einen Token
anzufordern. Wenn bei einem solchen Server selbst-signierte Zertifikate verwendet
werden, kann man allerdings **nicht** die Funktion `fetch` aus ECMAScript 2015
verwenden, sondern man muss `bru.sendRequest` verwenden und vom _Safe Mode_ in
den _Developer Mode_ wechseln. Voraussetzung dafür ist, dass auf dem eigenen
Entwicklungsrechner _Node_ installiert ist. Zum Wechseln in den _Developer Mode_
klickt man rechts oben auf _Safe Mode_ und anschließend auf den Radiobutton
_Developer Mode_.

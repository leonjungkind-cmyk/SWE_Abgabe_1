# Installationsanleitung

> Copyright 2016 - present [Jürgen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de), Hochschule Karlsruhe
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> at your option any later version
>
> This program is distributed in the hope that it will be useful
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
> GNU General Public License for more details
>
> You should have received a copy of the GNU General Public License
> along with this program. If not, see <https://www.gnu.org/licenses/>

> Mit Chrome und der Erweiterung _Markdown Viewer_ https://chromewebstore.google.com/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk?hl=de&pli=1
> kann man Markdown-Dateien mit der Endung `.md` schön lesen.
> Für diese Erweiterung muss man die Option _Zugriff auf Datei-URLs zulassen_
> aktivieren.

Allgemeine Hinweise:

- 16 GB RAM sind für eine _vernünftige_ Projektarbeit (d.h. für _Klausurpunkte_)
  sinnvoll. Bei Bedarf kann ein Notebook der Fakultät ausgeliehen werden.
- Nur in den ersten beiden Vorlesungswochen kann es Unterstützung bei
  Installationsproblemen geben.
- Diese Anleitung ist für _Windows 11_, damit jede/r Studierende auf dem
  eigenen oder einem ausgeliehenen Notebook flexibel arbeiten kann und nicht
  an die Poolräume gebunden ist. Für die Installation von Windows Home
  gibt es eine separate Installationsanleitung.
- Für _andere Betriebssysteme_ oder irgendwelche _Windows-Emulationen_
  sind Anpassungen notwendig.
  Bei über 160 Studenten (3. und 4. Semester sowie 3 Wahlpflichtfächer)
  kann es dafür leider **keine** Unterstützung geben:
  Welche Linux-Distribution? Welche Linux-Version? Welche macOS-Version?
  Ggf. gibt es genügend Notebooks zur Ausleihe.
- Die Installation sämtlicher Software erfolgt im Pfad `C:\Zimmermann`,
  damit sie in späteren Semestern leicht entfernt werden kann.
- In einem Webbrowser kann man z.B. mit der URL https://speed.cloudflare.com die
  Download- und die Upload-Geschwindigkeit testen.

## Inhalt

- [Windows](#windows)
- [Umgebungsvariable](#umgebungsvariable)
- [ZIP-Datei](#zip-datei)
- [Python](#python)
- [Node, npm und pnpm](#node-npm-und-pnpm)
- [Docker Desktop](#docker-desktop)
- [Build Tools für Visual Studio 2022](#build-tools-f%C3%BCr-visual-studio-2022)
- [Git](#git)
- [Visual Studio Code](#visual-studio-code)

## Windows

### Windows 11 25H2

Für _WSL 2_ und Docker Desktop (s.u.) ist Windows 11 25H2 notwendig. Die
aktuelle Version von Windows kann man ermitteln, indem man die [Windows-Taste]
drückt und `PC-Infos` eingibt. Dann sieht man die installierte Versionsnummer
im Feld _Version_. Mit dem Link
`https://www.microsoft.com/de-de/software-download/windows11`
kann man dann ggf. Windows aktualisieren.

Nachdem Windows (scheinbar) aktualisiert ist, muss man noch die Updates
installieren, die seit dem Erscheinen der gerade installierten Windows Version
zusätzlich erschienen sind. Die Updates kann man über das Windows-Menü in der
linken unteren Ecke des Desktops installieren.

Bevor man _PowerShell_, _Terminal_, _WSL 2_ usw. installiert, ist
ein Neustart des Rechners empfehlenswert.

### Update der Powershell

`PowerShell-7...-win-x64.msi` kann man von https://github.com/PowerShell/PowerShell/releases
herunterladen und installieren. Dabei wird die Umgebungsvariable `PATH` um den
Eintrag `C:\Program Files\PowerShell\7` ergänzt. Das kann man überprüfen,
indem man in einem _neuen_ Powershell-Fenster `$env:PATH` eingibt.

Jetzt sollte man die Umgebungsvariable `PATH` so setzen, dass `C:\Program Files\PowerShell\7`
_VOR_ dem Eintrag für Powershell Version 1 kommt. Dazu betätigt man die
`[Windows-Taste]` und gibt als Suchstring `Systemumgebungsvariablen bearbeiten`
ein.

### Terminal

_Terminal_ kann man von https://aka.ms/terminal-preview herunterladen und
installieren.

Alternativ kann man auch den Microsoft Store durch https://www.microsoft.com/de-de/store/top-free/apps/pc
benutzen oder über die [Windows-Taste] aus der Liste der Apps _Microsoft Store_
auswählen und nach _Terminal_ suchen.

### Update auf WSL 2

In einer Powershell als _Administrator_ gibt man folgendes Kommando ein, wofür
eine Internet-Verbindung notwendig ist. Anschließend empfiehlt sich ein Neustart.

```powershell
wsl --install
wsl --update
```

#### Bei Bedarf: Manuelles Update auf WSL 2

Falls das Update auf WSL 2 **nicht** funktioniert hat, kann man ein manuelles
Update durchführen, siehe https://docs.microsoft.com/windows/wsl/install-manual.
Dazu gibt man die beiden folgenden Kommandos ein, wobei nach dem 1. Kommando ein
Neustart des Rechners erforderlich sein kann. Nach dem 2. Kommando ist ein Neustart
des Rechners auf jeden Fall empfehlenswert.

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Als nächstes setzt man die Default-Version des _Windows Subsystem Linux_
durch `wsl --set-default-version 2`. Evtl erscheint eine Fehlermeldung
_"WSL 2 erfordert ein Update der Kernelkomponente ..."_. Dann muss der
Kernel auf V2 aktualisiert werden, indem von https://aka.ms/wsl2kernel
das Update-Paket beim entsprechenden Link heruntergeladen und installiert
wird.

### Nacharbeiten zu WSL 2

Nachdem WSL 2 installiert ist, kann man sich z.B. durch `wsl --list` die
(leere) Liste der installierten Linux-Distributionen anzeigen lassen.
Hier würde z.B. angezeigt werden, sobald _Docker Desktop_ installiert ist.

Ggf. kann man noch die Konfigurationsdatei `.wslconfig` im Verzeichnis
`C:\Users\<<MEINE_KENNUNG>>` mit z.B. folgendem Inhalt anlegen:

```powershell
[wsl2]
memory=8GB # max 8 GB RAM für die VM von WSL2
processors=4
```

## Umgebungsvariable

Vorab werden die notwendigen Umgebungsvariable gesetzt, damit nicht bei jeder
nachfolgenden Installation immer wieder einzelne Umgebungsvariable gesetzt werden
müssen.

`[Windows-Taste]` betätigen, dann als Suchstring `Systemumgebungsvariablen bearbeiten`
eingeben und auswählen.

Bei _Systemvariable_ (**nicht** bei _Benutzervariable_) folgende
Umgebungsvariable mit den jeweiligen Werten eintragen. Die Werte für `PATH`
_vor_ Pfaden mit _Leerzeichen_ eintragen.

| Name der Umgebungsvariable | Wert der Umgebungsvariable |
| -------------------------- | --------------------------- |
| `CARGO_HOME` | `C:\Zimmermann\cargo`
| `GIT_HOME` | `C:\Zimmermann\git` |
| `GRAPHVIZ_DOT` | `C:\Zimmermann\Graphviz\bin\dot.exe` |
| `HOME` | `C:\Users\<<MEINE_KENNUNG>>` |
| `K6_WEB_DASHBOARD` | `true` |
| `PATH` | `C:\Zimmermann\Python` <br /> `C:\Zimmermann\Python\Scripts` <br /> `%CARGO_HOME%\bin` <br /> `C:\Zimmermann\node` <br /> `%GIT_HOME%\cmd` <br /> `%GIT_HOME%\bin` <br /> `C:\Zimmermann\k6` <br /> `C:\Zimmermann\Graphviz\bin` |

## ZIP-Datei

`C:\Zimmermann\Git` und `C:\Zimmermann\node` löschen, falls sie noch von letztem Semester
vorhanden sind. Von ILIAS packt man die ZIP-Datei `Zimmermann.zip` unter `C:\Zimmermann` aus.

## Python

### Installation von Python für Windows

Von `https://www.python.org/downloads/windows` lädt man sich die .EXE-Datei für
die aktuelle 64-Bit-Version herunter; **KEINE** Alpha- oder Beta-Version, weil
später ein Docker-Image gebaut wird. Die .EXE-Datei führt man aus und macht
dabei folgende Eingaben:

- _Customize Installation_:
  - _Documentation_: Haken entfernen
  - _Tcl/Tk_: Haken entfernen
  - _Test suite_: Haken entfernen
- _Install for all users_ anklicken
- _Customize install location_: `C:\Zimmermann\Python`

Nach Abschluss sollte man die Installation testen:

```powershell
python --version
python
    exit()
python -m pip install --upgrade pip
pip --version
```

### uv als Package und Project Manager

_uv_ als Package und Project Manager ist laut Homepage "extremely fast", implementiert
in Rust und hat bei GitHub über 40.000 Starts. uv wird folgendermaßen installiert:

```shell
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Bei Linux und MacOS muss man die Umgebungsvariable `PATH` um `~/.local/bin` ergänzen.

### Rust und Cargo für FastAPI?

Die Umgebungsvariable `CARGO_HOME` setzt man z.B. auf C:\Zimmermann\cargo und
ergänzt die Umgebungsvariable `PATH` um %CARGO_HOME%\bin. Danach lädt man sich
von https://rustup.rs die Datei `rustup-init.exe` herunter und führt sie aus.

```shell
rustc --version
cargo --version
```

Mit `rustup update` kann man eine vorhandene Rust-Installation aktualisieren.

## Node, npm und pnpm

### Node und npm

In einer Powershell die nachfolgenden Kommandos eingeben:

```powershell
Get-Command node
node --version
Get-Command npm
npm --version
```

### pnpm

`pnpm` (performant node package manager) wird mit `npm` (s.o.) installiert.

```shell
npm r -g pnpm
npm i -g pnpm

pnpm --version
```

## Docker Desktop

### Docker Desktop deinstallieren

Falls aus bereits eine alte Version von Docker Desktop installiert ist, sollte
man diese zuerst deinstallieren:

```shell
# Ueberpruefen, dass keine Container laufen:
docker ps --all

# vorhandene Container ggf. beenden und entfernen:
docker kill <container-id>
docker rm <container-id>

# Alle Images und alle anonymen Volumes loeschen
docker system prune --volumes --all
```

Jetzt kann man über `[Windows-Taste]` und `Apps und Features` das Produkt
Docker Desktop deinstallieren.

Dabei bleiben evtl. alte (Konfigurations-) Dateien erhalten, die man entfernen
sollte, um mit einem sauberen Entwicklungsstand zu starten. Dazu muss man über
den _Task-Manager_ (`<Strg><Alt><Delete>`) evtl. den Dienst _Docker Desktop_ und
sonstige Dienste, bei denen im Namen "docker" enthalten ist, beenden. Nun kann
man mit den nachfolgenden Kommandos noch evtl. vorhandene Verzeichnisse in Windows
löschen:

```powershell
Remove-Item -Force -Recurse $env:USERPROFILE\.docker
Remove-Item -Force -Recurse $env:USERPROFILE\.kube
Remove-Item -Force -Recurse $env:LOCALAPPDATA\Docker
Remove-Item -Force -Recurse $env:APPDATA\Docker
Remove-Item -Force -Recurse $env:APPDATA\'Docker Desktop'
```

Für weitere Verzeichnisse sind Administrator-Rechte notwendig und es wird
angenommen, dass der Administrator-User, mit dem ursprünglich Docker Desktop
installiert wurde, `Administrator` heißt. Dann kann man in einer PowerShell
unter dem User `Administrator` folgende Kommandos absetzen:

```powershell
Remove-Item -Force -Recurse 'C:\Program Files\Docker'
Remove-Item -Force -Recurse C:\ProgramData\DockerDesktop
Remove-Item -Force C:\ProgramData\Docker
Remove-Item -Force -Recurse C:\Users\Administrator\.docker
Remove-Item -Force -Recurse C:\Users\Administrator\AppData\Local\Docker
Remove-Item -Force C:\Users\${env:USERNAME}\AppData\Local\'Docker Desktop Installer'
Remove-Item -Force -Recurse C:\Users\Administrator\AppData\Roaming\Docker
Remove-Item -Force -Recurse C:\Users\Administrator\AppData\Roaming\'Docker Desktop'
Remove-Item -Force C:\Users\${env:USERNAME}\Desktop\'Docker Desktop.lnk'
```

### Docker Desktop installieren und konfigurieren

Die _Community Edition_ von _Docker Desktop for Windows_ kann man von
https://docs.docker.com/desktop/release-notes/ herunterladen
und installieren. Dabei wird die Umgebungsvariable `PATH` um den Eintrag
`C:\Program Files\Docker\Docker\resources\bin` ergänzt.

### Docker Desktop starten und testen

_Docker Desktop_ startet man folgendermaßen:

- Im Explorer in das Verzeichnis `C:\Program Files\Docker\Docker` wechseln.
- `Docker Desktop.exe` als `Administrator` ausführen, d.h. Doppelklick, falls
  man eine Benutzerkennung mit Administrator-Rechten benutzt oder die rechte
  Maustaste für das Kontextmenü benutzen und _Als Administrator ausführen_
  auswählen.

Im _System Tray_ (rechts unten in der _Taskleiste_) ist nun das Docker-Icon
(_Whale_) zu sehen. Es ist empfehlenswert, eine Verknüpfung zu
`Docker Desktop.exe` in der Taskleiste oder im Startmenü einzurichten.

Jetzt kann man mit dem nachfolgenden Kommando einen einfachen Test
durchführen und sich Informationen zur installierten Version einschließlich
Docker Compose ausgeben lassen:

```shell
# Windows:
Get-Command docker

# macOS:
which docker

docker info
```

`docker info` zeigt dabei u.a. die Plugins _buildx_, _compose_ und _sbom_ an.

### Registrierung für "Docker Hardenend Images" und Docker Scout

Um Docker Hardenend Images herunterladen zu können (s.u. `docker pull dhi.io/...`)
und Docker Scout zur Analyse für Sicherheitslücken nutzen zu können, muss man sich
bei https://hub.docker.com registrieren.

### Docker Images

Die nachfolgenden Kommandos werden in einer neuen Powershell abgesetzt, um Images
zu installieren. Wenn man _GitHub Actions_ benutzen wird, braucht man nicht das
Jenkins-Image.

```shell
docker pull docker/dockerfile:1.22.0
docker pull hadolint/hadolint:v2.14.0-debian
docker pull dhi.io/python:3.14.3-debian13
docker pull python:3.14.3-slim-trixie
docker pull python:3.14.3-alpine3.23
docker pull ghcr.io/astral-sh/uv:0.10.10-python3.14-dhi
docker pull ghcr.io/astral-sh/uv:0.10.10-python3.14-trixie-slim
docker pull ghcr.io/astral-sh/uv:0.10.10-python3.14-alpine3.23
docker pull dhi.io/postgres:18.3-debian13
docker pull axllent/mailpit:v1.29.3
docker pull dhi.io/keycloak:26.5.5-debian13
docker pull sonarqube:26.3.0.120487-community
docker pull dhi.io/bun:1.3.10-debian13
docker pull oven/bun:1.3.10-slim
docker pull oven/bun:1.3.10-alpine
docker pull prom/prometheus:v3.10.0
docker pull grafana/grafana:12.4.1
docker pull grafana/grafana:12.3.5
```

### Docker Dashboard

Falls man das _Docker Dashboard_ geschlossen hat, kann man es wieder öffnen,
indem man das Whale-Icon (s.o.) im _System Tray_ anklickt. Im Menüpunkt
_Images_ kann man die oben installierten Images sehen.

## Build Tools für Visual Studio 2022

Die _Build Tools_ mit insbesondere dem C++ Compiler sind für z.B. _node-gyp_ erforderlich.

_Build Tools_ kann man von https://visualstudio.microsoft.com/de/downloads herunterladen.
Wenn man die heruntergeladene `.exe`-Datei ausführt, wählt man
_Desktopentwicklung mit C++_, _Windows 11 SDK_ und _Windows 10 SDK_ aus, indem
man den Haken in der jeweiligen Checkbox setzt und auf den Button _Installieren_
klickt.

## Git

### .gitconfig

Falls es die Datei `C:\Users\<<MEINE_KENNUNG>>\.gitconfig` nicht gibt,
wird sie durch diese beiden Kommandos in der Powershell erstellt und verwendet
dabei den eigenen Namen und die eigene Email-Adresse:

```powershell
git config --global user.name "Max Mustermann"
git config --global user.email Max.Mustermann@acme.com
```

Anschließend kann man `C:\Users\<<MEINE_KENNUNG>>\.gitconfig`
in einem Editor ggf. um folgende Zeilen ergänzen:

```text
[push]
    default = simple
```

### Git testen

In einer neuen Powershell folgendes Kommando eingeben:

```powershell
Get-Command git
git --version
```

## Visual Studio Code

### Installation

Visual Studio Code kann man von https://code.visualstudio.com/Download herunterladen.

Natürlich kann auch WebStorm, IntelliJ IDEA, Visual Studio oder ... benutzt werden.

### Erweiterungen

Installation von _Erweiterungen_ (Menüpunkt am linken Rand), z.B.:

- Apollo GraphQL
- AsciiDoc
- autoDocstring
- Better Comments
- Black Formatter
- Bruno
- Container Tools
- Docker
- DotENV
- EditorConfig for VS Code
- Error Lens
- ESLint
- Even Better TOML
- German Language Pack for Visual Studio Code
- GitLens
- Git Graph
- Git History
- GitHub Copilot
- GraphQL: Language Feature Support
- JavaScript and TypeScript Nightly
- MarkdownLint
- Material Icon Theme
- PlantUML
- PostgreSQL (von Microsoft)
- Prettier - Code formatter
- Pretty TypeScript Errors
- Pylance
- Python
- Rainbow CSV
- Ruff
- Todo Tree
- ty
- TypeScript Importer
- Version Lens
- Vitest
- YAML

### Einstellungen

Man öffnet die Einstellungen über das Icon am linken Rand ganz unten und wählt den
Menüpunkt `Einstellungen` oder `Settings`. Danach im Suchfeld folgendes eingeben
und jeweils den Haken setzen:

- editor.foldingImportsByDefault
- eslint.enable
- typescript.inlayHints.variableTypes.enabled
- typescript.inlayHints.propertyDeclarationTypes.enabled
- typescript.inlayHints.parameterTypes.enabled
- typescript.inlayHints.functionLikeReturnTypes.enabled

# Empfohlene Vorgehensweise für das Lernen von FastAPI

> Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
> along with this program. If not, see <http://www.gnu.org/licenses/>.

## EINDRINGLICHE EMPFEHLUNG

- Schrittweise vorgehen, um die Komplexität zu reduzieren
- Iteratives Lernen: bei jedem Schritt die Funktionalität verstehen, bevor man weiter macht
- Am Projektende ein Code-Review durch _Codex_ und/oder _Copilot_ durchführen lassen

## Elementare Infrastruktur und einfacher Server

- VS Code mit Erweiterungen
- GET-Request durch FastAPI mit "Hello World" als dict
- uv, .venv, pyproject.toml und Source-Layout
- pyproject.toml für uv mit dependencies und Skript für Serverstart
- GET-Request von Webbrowser aufrufen
- Server mit TLS
- config mit TOML für HTTPS-Port sowie TLS (später: Logging, DB-Zugriff, Mail, Keycloak)

## Codeanalyse, Formatierung, Typprüfung und Sicherheit

- Ruff
- ty
- SonarQube als Docker Container
- uv tree --outdated --all-groups --depth=1
- uv pip list --outdated
- pysentry und pip-audit
- OWASP Dependency Check

## Infrastruktur

- Verzeichnisstruktur, Schichtenarchitektur und DDD: Service auslagern, Hello -> Patient, DI
- Gruppierung und Aufteilung von Router
- Request- und Response-Body komprimieren durch fastapi.middleware.gzip
- Security-Header: z.B. STS, nosniff, ..., CORS
  - CSP (Content Security Policy) ist nur bei HTML sinnvoll
  - Schutz vor XSS (Cross-Site Scripting) ist nur bei HTML sinnvoll

## REST-Schnittstelle, DB-Zugriff, Validierung, Bruno und Testen

- Logging durch loguru
- Router mit Pfad- und Query-Parameter
- Statuscodes
- Header: Location, If-Non-Match, SPÄTER: If-Match, ETag
- OR-Mapping mit SQLAlchemy sowie DB-Server durch PostgreSQL mit "Hardened" Image
  (einschl. Fetch-Join, SPÄTER: Transaktionen, Lost Updates)
- Fehlerbehandlung, z.B. 404, 412, 422, 428
- docstrings mit Markdown-Syntax für API-Dokumentation innerhalb von mkdocs
- POST-Request mit DTOs einschließlich Validierung durch pydantic
- Bruno
- DB neu laden
- Unit-Tests
- Integrationstests mit pytest und httpx
- CI mit z.B. GitHub Actions

## Docker

- Dockerfile mit "Hardened" Image
- Docker Compose

## Weitere Funktionalitäten

- Mail durch smtplib
- Keycloak für OIDC durch python-keycloak
- evtl. Keycloak neu laden
- PUT einschl. Vermeidung von "Lost Updates" sowie bedingte GET-Requests
- DELETE
- GraphQL durch Strawberry: "Code-first"-Ansatz für Query und Mutation
- mkdocs und PlantUML für Dokumentation
- Lasttests mit locust

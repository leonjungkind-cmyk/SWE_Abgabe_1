# Code-Walkthrough: Integrationstests

Dieses Dokument erklärt jede Testdatei des Projekts – Block für Block, Zeile für Zeile.
Reihenfolge: Gemeinsame Hilfsmittel → einfache Tests → REST → GraphQL → Security → Lasttest

Disclaimer: Diese Erklärung ist von Claude Code generiert worden.

---

## Inhaltsverzeichnis

1. [Projektstruktur der Tests](#1-projektstruktur-der-tests)
2. [common_test.py – Gemeinsame Basisdaten](#2-common_testpy--gemeinsame-basisdaten)
3. [simple_test.py – Sanity-Tests](#3-simple_testpy--sanity-tests)
4. [conftest.py – pytest-Fixtures](#4-conftestpy--pytest-fixtures)
5. [REST-Tests](#5-rest-tests)
   - [get_by_id_test.py](#51-get_by_id_testpy)
   - [get_test.py](#52-get_testpy)
   - [post_test.py](#53-post_testpy)
   - [put_test.py](#54-put_testpy)
   - [delete_test.py](#55-delete_testpy)
   - [health_test.py](#56-health_testpy)
6. [GraphQL-Tests](#6-graphql-tests)
   - [query_test.py](#61-query_testpy)
   - [mutation_test.py](#62-mutation_testpy)
7. [Security-Tests](#7-security-tests)
   - [login_test.py](#71-login_testpy)
8. [Lasttest – locustfile.py](#8-lasttest--locustfilepy)

---

## 1. Projektstruktur der Tests

```
tests/
├── integration/
│   ├── common_test.py          ← gemeinsame URLs, Credentials, Hilfsfunktionen
│   ├── simple_test.py          ← minimaler Sanity-Test, Einstiegspunkt
│   ├── certificate.crt         ← TLS-Zertifikat für HTTPS-Verbindungen
│   ├── rest/
│   │   ├── conftest.py         ← Fixtures: DB/Keycloak einmalig laden
│   │   ├── get_by_id_test.py   ← GET /rest/kunden/{id}
│   │   ├── get_test.py         ← GET /rest/kunden?email=...&nachname=...
│   │   ├── post_test.py        ← POST /rest
│   │   ├── put_test.py         ← PUT /rest/kunden/{id}
│   │   ├── delete_test.py      ← DELETE /rest/kunden/{id}
│   │   └── health_test.py      ← GET /health/liveness & /health/readiness
│   ├── graphql_api/
│   │   ├── conftest.py         ← gleiche Fixtures wie REST
│   │   ├── query_test.py       ← GraphQL Queries (Lesen)
│   │   └── mutation_test.py    ← GraphQL Mutations (Schreiben)
│   └── security/
│       └── login_test.py       ← POST /auth/token (Token holen)
└── lasttest/
    └── locustfile.py           ← Lasttest mit Locust
```

Alle Tests sind **Integrationstests**: Sie laufen gegen einen echten, laufenden Server
auf `https://127.0.0.1:8000`. Es gibt keine Unit-Tests mit gemockten Abhängigkeiten.

---

## 2. common_test.py – Gemeinsame Basisdaten

Diese Datei ist kein eigenes Test-Modul, sondern eine **Sammlung von Konstanten und
Hilfsfunktionen**, die alle anderen Testdateien per Import nutzen.

### Konstanten

```python
schema: Final = "https"
port: Final = 8000
host: Final = "127.0.0.1"      # explizit IPv4, kein "localhost" (vermeidet IPv6-Fallback unter Windows)
base_url: Final = f"{schema}://{host}:{port}"

rest_path:    Final = "/rest/kunden"
graphql_path: Final = "/graphql"
token_path:   Final = "/auth/token"
health_url:   Final = f"{base_url}/health"
```

`Final` aus dem `typing`-Modul markiert Variablen als unveränderlich – sie können nach
der Zuweisung nicht neu gebunden werden. Das macht Tippfehler bei Neuzuweisungen
zur Compilezeit sichtbar.

### TLS-Kontext

```python
certificate: Final = str(Path("tests") / "integration" / "certificate.crt")
ctx = create_default_context(cafile=certificate)
```

Da der Server ein **selbst-signiertes Zertifikat** verwendet, würde ein normales
`httpx.get(url, verify=True)` mit einem SSL-Fehler scheitern. Stattdessen wird ein
eigener TLS-Kontext (`ctx`) mit dem bekannten Zertifikat erstellt und an jeden Request
übergeben (`verify=ctx`).

### `login()` – REST-Login

```python
def login(username: str = username_admin, password: str = password_admin) -> str:
    login_data: Final = {"username": username, "password": password}
    response: Final = post(f"{base_url}{token_path}", json=login_data, verify=ctx, timeout=timeout)
    ...
    token: Final = response_body.get("token")
    return token
```

Sendet einen POST an `/auth/token` und gibt das JWT-Token als String zurück.
Default-Credentials sind `admin` / `p`. Alle REST-Tests rufen diese Funktion im
`# arrange`-Abschnitt auf.

### `login_graphql()` – GraphQL-Login

```python
def login_graphql(...) -> str:
    login_query: Final = {
        "query": f'mutation {{ login(username: "{username}", password: "{password}") {{ token }} }}'
    }
    response: Final = post(f"{base_url}{graphql_path}", json=login_query, ...)
    token: Final = response_body.get("data").get("login").get("token")
    return token
```

Beim GraphQL-Login wird der Token über eine **GraphQL-Mutation** geholt, nicht über
einen separaten REST-Endpunkt. Die Antwort ist deshalb tiefer verschachtelt: `data → login → token`.

### `db_populate()` und `keycloak_populate()`

```python
def db_populate() -> None:
    token: Final = login()
    headers: Final = {"Authorization": f"Bearer {token}"}
    response: Final = post(f"{base_url}{db_populate_path}", headers=headers, verify=ctx)
    assert response.status_code == HTTPStatus.OK
```

Diese Hilfsfunktionen rufen Dev-Endpunkte auf (`/dev/db_populate`,
`/dev/keycloak_populate`), die die Datenbank und Keycloak mit Testdaten befüllen.
Sie werden von den `conftest.py`-Fixtures vor jedem Testlauf aufgerufen.

---

## 3. simple_test.py – Sanity-Tests

```python
@mark.simple
def test_simple() -> None:
    assert True
```

Ein Test, der immer besteht. Er dient als **Smoke-Test**, um sicherzustellen, dass
pytest überhaupt läuft und die Testinfrastruktur funktioniert.

```python
@mark.skip(reason="Fail")
def test_always_fail() -> None:
    assert not True
```

Ein absichtlich fehlschlagender Test, der mit `@mark.skip` übersprungen wird. Er
zeigt, wie man Tests gezielt deaktiviert (z.B. für bekannte Bugs oder offene Features).

### Marker-Syntax

```python
@mark.simple     # eigener Marker, in pyproject.toml registriert
@mark.skip(reason="...")  # eingebauter pytest-Marker
```

Marker ermöglichen das gezielte Ausführen einer Teilmenge: `pytest -m simple` führt
nur mit `@mark.simple` markierte Tests aus.

---

## 4. conftest.py – pytest-Fixtures

Jede Test-Gruppe (`rest/`, `graphql_api/`) hat eine eigene `conftest.py`.
pytest lädt diese Datei automatisch vor den Tests im gleichen Verzeichnis.

```python
@fixture(scope=session_scope, autouse=True)
def check_readiness_per_session() -> None:
    check_readiness()
```

- `scope="session"`: Das Fixture wird **einmal pro gesamtem Testlauf** ausgeführt,
  nicht einmal pro Test. Das spart Zeit bei teuren Operationen.
- `autouse=True`: Das Fixture wird **automatisch** für jeden Test in diesem Verzeichnis
  aktiviert, ohne dass der Test es explizit anfordern muss.

```python
@fixture(scope=session_scope, autouse=True)
def populate_per_session() -> None:
    db_populate()       # Testdaten in die DB laden
    keycloak_populate() # Testbenutzer in Keycloak laden
```

Dieses Fixture stellt sicher, dass **vor dem ersten Test** bekannte, reproduzierbare
Testdaten vorhanden sind. Ohne dieses Fixture würden Tests je nach DB-Zustand
unterschiedliche Ergebnisse liefern.

---

## 5. REST-Tests

### Allgemeines Muster (AAA)

Alle REST-Tests folgen dem **Arrange-Act-Assert**-Muster:

```python
def test_irgendwas() -> None:
    # arrange – Vorbereitung: Token holen, Daten zusammenstellen
    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    # act – Aktion: den eigentlichen HTTP-Request absetzen
    response = get(f"{rest_url}/1", headers=headers, verify=ctx)

    # assert – Überprüfung: Ergebnis kontrollieren
    assert response.status_code == HTTPStatus.OK
```

---

### 5.1 get_by_id_test.py

Testet `GET /rest/kunden/{id}`.

```python
@mark.parametrize("kunde_id", [30, 1, 20])
def test_get_by_id_admin(kunde_id: int) -> None:
```

`@mark.parametrize` führt den gleichen Test mit mehreren Eingabewerten aus.
Hier wird der Test dreimal ausgeführt – mit den IDs 30, 1 und 20. Das spart
doppelten Code für strukturell identische Testfälle.

**Abgedeckte Szenarien:**

| Testfunktion | Was wird geprüft |
|---|---|
| `test_get_by_id_admin` | Admin findet Kunden mit gültiger ID → 200 |
| `test_get_by_id_nicht_gefunden` | Nicht-existente ID → 404 |
| `test_get_by_id_kunde` | Kunde sieht eigenen Datensatz → 200 |
| `test_get_by_id_nicht_erlaubt` | Kunde sieht fremden Datensatz → 403 |
| `test_get_by_id_nicht_erlaubt_nicht_gefunden` | Nicht-existente ID als Kunde → 403 (kein Datenleck) |
| `test_get_by_id_ungueltiger_token` | Manipulierter Token → 401 |
| `test_get_by_id_ohne_token` | Kein Token → 401 |
| `test_get_by_id_etag` | Gültiger `If-None-Match`-Header → 304 Not Modified |
| `test_get_by_id_etag_ungueltig` | Ungültiger ETag → normaler 200-Response |

**ETag-Test im Detail:**

```python
headers = {
    "Authorization": f"Bearer {token}",
    "If-None-Match": '"0"',   # ETag-Wert: Versionsnummer in Anführungszeichen
}
response = get(f"{rest_url}/{kunde_id}", headers=headers, verify=ctx)
assert response.status_code == HTTPStatus.NOT_MODIFIED  # 304
assert not response.text                                # kein Body
```

Wenn der Client einen ETag schickt, der mit der aktuellen Version übereinstimmt,
antwortet der Server mit `304 Not Modified` und **ohne Body** – spart Bandbreite.

---

### 5.2 get_test.py

Testet `GET /rest/kunden?email=...` und `GET /rest/kunden?nachname=...`
sowie `GET /rest/kunden/nachnamen/{teil}`.

```python
@mark.parametrize("email", ["mueller@example.de", "schmidt@example.de"])
def test_get_by_email(email: str) -> None:
    params = {"email": email}
    response = get(rest_url, params=params, headers=headers, verify=ctx)
    ...
    content: Final = response_body["content"]  # paginierte Antwort
    assert len(content) == 1
    assert content[0].get("email") == email
```

Query-Parameter werden als `params={"schlüssel": "wert"}` übergeben. `httpx`
hängt sie automatisch als URL-Parameter an: `/rest/kunden?email=mueller@example.de`.

Die Antwort ist **paginiert** – der Response-Body enthält ein `content`-Array,
keine direkte Liste von Kunden.

---

### 5.3 post_test.py

Testet `POST /rest` zum Anlegen neuer Kunden.

```python
neuer_kunde: Final = {
    "nachname": "Neurest",
    "email": "neurest@rest.de",
    "adresse": {
        "strasse": "Teststraße",
        "hausnummer": "1",
        "plz": "99999",
        "ort": "Testort",
    },
}
response = post(rest_url, json=neuer_kunde, headers=headers, verify=ctx)

assert response.status_code == HTTPStatus.CREATED   # 201
location: Final = response.headers.get("Location")  # z.B. /rest/kunden/1042
assert search("[1-9][0-9]*$", location) is not None # endet auf eine positive Zahl
assert not response.text                            # kein Body bei 201
```

`search("[1-9][0-9]*$", location)` prüft per Regex, dass die `Location`-URL
auf eine valide ID (positive ganze Zahl) endet.

**Abgedeckte Fehlerfälle:**

| Testfunktion | Was wird geprüft |
|---|---|
| `test_post` | Valider Kunde → 201, Location-Header mit ID |
| `test_post_ungueltig` | Ungültige Email + PLZ → 422, Fehlermeldung nennt `email` und `plz` |
| `test_post_email_existiert` | Bereits vorhandene Email → 422 |
| `test_post_ungueltige_json` | String statt Dictionary → 422 mit Pydantic-Meldung |

---

### 5.4 put_test.py

Testet `PUT /rest/kunden/{id}` zum Aktualisieren von Kundendaten.

Ein PUT benötigt zwingend den `If-Match`-Header mit der aktuellen Versionsnummer
(optimistische Nebenläufigkeitskontrolle):

```python
headers = {
    "Authorization": f"Bearer {token}",
    "If-Match": '"0"',   # Versionsnummer in doppelten Anführungszeichen
}
response = put(f"{rest_url}/{kunde_id}", json=geaenderter_kunde, headers=headers, verify=ctx)
assert response.status_code == HTTPStatus.NO_CONTENT   # 204
```

**Alle Versionsnummer-Fehlerfälle:**

| Szenario | Header-Wert | Erwarteter Statuscode |
|---|---|---|
| Korrekter ETag | `"0"` | 204 No Content |
| Fehlender Header | – | 428 Precondition Required |
| Alte Versionsnr. | `"-1"` | 412 Precondition Failed |
| Nicht-numerisch | `"xy"` | 412 Precondition Failed |
| Ohne Anführungszeichen | `0` | 412 Precondition Failed |

---

### 5.5 delete_test.py

Testet `DELETE /rest/kunden/{id}`.

```python
def test_delete_nicht_gefunden() -> None:
    kunde_id: Final = 999999
    response = delete(f"{rest_url}/{kunde_id}", headers=headers, verify=ctx)
    assert response.status_code == 204   # ebenfalls 204, nicht 404
```

DELETE ist **idempotent**: Das Löschen einer nicht-existenten ID ist kein Fehler –
der gewünschte Endzustand (Kunde nicht vorhanden) ist bereits erreicht. Deshalb
gibt auch ein nicht-gefundener Kunde `204 No Content` zurück.

---

### 5.6 health_test.py

Testet `/health/liveness` und `/health/readiness`.

```python
def test_liveness() -> None:
    response = get(f"{health_url}/liveness", verify=ctx)
    assert response.status_code == HTTPStatus.OK
    assert response_body.get("status") == "up"

def test_readiness() -> None:
    response = get(f"{health_url}/readiness", verify=ctx)
    assert response_body.get("db") == "up"
```

- **Liveness**: Ist der Server-Prozess am Leben?
- **Readiness**: Ist der Server bereit, Anfragen anzunehmen (DB-Verbindung aktiv)?

Health-Endpunkte benötigen **keinen Auth-Token** – sie sollen auch von
Monitoring-Systemen erreichbar sein.

---

## 6. GraphQL-Tests

### Grundprinzip GraphQL

Im Gegensatz zu REST werden alle GraphQL-Anfragen als **POST** an `/graphql`
gesendet. Die eigentliche Operation steht im Request-Body als JSON-Objekt mit
dem Schlüssel `"query"`:

```python
query = {
    "query": """
        {
            kunde(kundeId: "20") {
                nachname
                email
            }
        }
    """
}
response = post(graphql_url, json=query, headers=headers, verify=ctx)
```

Der HTTP-Statuscode ist bei GraphQL **immer 200**, auch bei Fehlern. Fehler stehen
im `errors`-Feld des Response-Bodys, Ergebnisse im `data`-Feld.

---

### 6.1 query_test.py

Testet lesende GraphQL-Operationen.

**Einzelner Kunde per ID:**

```python
query = {
    "query": """
        {
            kunde(kundeId: "20") {
                version
                nachname
                email
                adresse { plz  ort }
                bestellungen { produktname  menge }
            }
        }
    """
}
data = response_body["data"]
kunde = data["kunde"]
assert isinstance(kunde, dict)
assert response_body.get("errors") is None
```

Der Client wählt selbst, **welche Felder** er haben möchte – das ist ein
Kernprinzip von GraphQL. Der Server liefert nur die angeforderten Felder zurück.

**Nicht-gefundener Kunde bei GraphQL:**

```python
# Bei GraphQL ist "nicht gefunden" KEIN Fehler im errors-Array:
assert response_body["data"]["kunde"] is None   # data vorhanden, aber null
assert response_body.get("errors") is None      # kein errors-Eintrag
```

GraphQL unterscheidet zwischen **technischen Fehlern** (stehen in `errors`) und
**fachlichen Leer-Ergebnissen** (stehen als `null` in `data`).

---

### 6.2 mutation_test.py

Testet schreibende GraphQL-Operationen.

```python
query = {
    "query": """
        mutation {
            create(
                kundeInput: {
                    nachname: "Nachnamegraphql"
                    email: "testgraphql@graphql.de"
                    adresse: {
                        strasse: "Graphqlstraße"
                        hausnummer: "1"
                        plz: "99999"
                        ort: "Graphqlort"
                    }
                }
            ) {
                id
            }
        }
    """
}
assert isinstance(response_body["data"]["create"]["id"], int)
```

Das Schlüsselwort `mutation` statt `query` kennzeichnet eine schreibende Operation.
Der Rückgabewert der Mutation (`{ id }`) gibt an, welche Felder des neu angelegten
Kunden zurückgegeben werden sollen.

**Validierungsfehler bei GraphQL:**

```python
# Ungültige Daten → errors-Array mit einem Eintrag, data ist null
assert response_body["data"] is None
errors = response_body["errors"]
assert isinstance(errors, list)
assert len(errors) == 1
```

---

## 7. Security-Tests

### 7.1 login_test.py

Testet `POST /auth/token` direkt.

```python
@mark.login
def test_login_admin() -> None:
    token: Final = login()
    assert isinstance(token, str)
    assert token               # nicht leer
```

```python
def test_login_ungueltige_passwort() -> None:
    login_data = {"username": username_admin, "password": "UNGÜLTIGES_PASSWORT"}
    response = post(f"{base_url}{token_path}", json=login_data, verify=ctx, timeout=timeout)
    assert response.status_code == HTTPStatus.UNAUTHORIZED   # 401
```

```python
def test_login_ohne_anmeldedaten() -> None:
    login_data: Final[dict[str, str]] = {}   # leeres Dictionary
    response = post(...)
    assert response.status_code == HTTPStatus.UNAUTHORIZED   # 401
```

Diese Tests prüfen die **Authentifizierungsschicht** unabhängig vom Kundendaten-CRUD.
Der Typ `dict[str, str]` im letzten Test ist eine explizite Typisierung: ein Dictionary
mit String-Schlüsseln und String-Werten (hier leer, um den Fehlerpfad zu testen).

---

## 8. Lasttest – locustfile.py

Locust ist ein Python-Framework für Lasttests. Statt Test-Assertions gibt es
**simulierte Benutzer**, die reale Anfragen in hoher Frequenz absenden.

### Starten

```
uvx locust -f tests/lasttest/locustfile.py
# Weboberfläche: http://localhost:8089
# Host: https://localhost:8000
```

### Aufbau

```python
class GetUser(HttpUser):
    wait_time = constant_throughput(0.1)   # 0.1 Iterationen/Sekunde pro User = 10s Pause
```

`HttpUser` ist die Basisklasse für simulierte Benutzer. `constant_throughput(0.1)`
begrenzt auf 0.1 Task-Iterationen pro Sekunde pro User.

### on_start – Login einmalig pro User

```python
def on_start(self) -> None:
    self.client.verify = False   # selbst-signiertes Zertifikat ignorieren
    response = self.client.post("/auth/token", json={"username": "admin", "password": "p"})
    token = response.json()["token"]
    self.client.headers = {"Authorization": f"Bearer {token}"}
```

`on_start` wird **einmalig** ausgeführt, wenn ein virtueller User startet. Der Token
wird im Client-Header gespeichert, damit alle folgenden Requests automatisch
authentifiziert sind.

### @task – gewichtete Aufgaben

```python
@task(100)
def get_id(self) -> None:
    for kunde_id in [1, 20, 30, 40, 50, 60]:
        self.client.get(f"/rest/{kunde_id}")

@task(200)
def get_nachname(self) -> None:
    for teil in ["a", "i", "n", "e", "v"]:
        self.client.get("/rest", params={"nachname": teil})

@task(150)
def get_email(self) -> None:
    ...
```

Die Zahl in `@task(N)` ist ein **relatives Gewicht**. Mit Gewichtungen 100 : 200 : 150
werden diese drei Aufgaben im Verhältnis 2 : 4 : 3 ausgeführt. `get_nachname` wird
also doppelt so oft wie `get_id` aufgerufen, um einen realistischeren Lastmix zu
simulieren.

---

*Leon Jungkind*

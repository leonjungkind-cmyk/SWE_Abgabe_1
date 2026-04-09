# Write-Walkthrough: Kundenverwaltung (Schreiben)

Dieses Dokument erklärt alle Dateien, die am **Anlegen, Aktualisieren und Löschen**
von Kunden beteiligt sind – Zeile für Zeile.

**Disclaimer: Diese Erklärung ist von Claude Code Generiert worden!**

---

## Inhaltsverzeichnis

1. [Überblick: Datenfluss beim Schreiben](#1-überblick-datenfluss-beim-schreiben)
2. [Pydantic-Modelle (Eingabe-Validierung)](#2-pydantic-modelle-eingabe-validierung)
   - [adresse\_model.py](#21-routeradresse_modelpy)
   - [kunde\_model.py](#22-routerkunde_modelpy)
   - [kunde\_update\_model.py](#23-routerkunde_update_modelpy)
3. [Write-Service](#3-write-service)
   - [kunde\_write\_service.py](#31-servicekunde_write_servicepy)
4. [Write-Router](#4-write-router)
   - [kunde\_write\_router.py](#41-routerkunde_write_routerpy)

---

## 1. Überblick: Datenfluss beim Schreiben

```shell
POST /rest/kunden          →  neuen Kunden anlegen
PUT  /rest/kunden/{id}     →  vorhandenen Kunden aktualisieren
DELETE /rest/kunden/{id}   →  Kunden löschen
```

### POST – neuen Kunden anlegen

```shell
HTTP POST /rest/kunden
  Body: { "nachname": "...", "email": "...", "adresse": {...} }
        │
        ▼
1. KundeModel (Pydantic)       ← validiert JSON automatisch
        │ .to_kunde()
        ▼
2. Kunde-Entity                ← SQLAlchemy-Objekt (noch ohne ID)
        │
        ▼
3. KundeWriteService.create()  ← prüft ob Email schon existiert
        │
        ▼
4. KundeRepository.create()    ← session.add() + session.flush()
        │                         → DB vergibt ID
        ▼
5. KundeDTO                    ← zurück mit generierter ID
        │
        ▼
6. HTTP 201 Created
   Location: /rest/kunden/42
```

### PUT – Kunden aktualisieren

```shell
HTTP PUT /rest/kunden/42
  Header: If-Match: "0"          ← Versionsnummer (ETag)
  Body: { "nachname": "...", "email": "..." }
        │
        ▼
1. Router prüft If-Match-Header  ← fehlt → 428, ungültig → 412
        │
        ▼
2. KundeUpdateModel (Pydantic)   ← validiert JSON
        │ .to_kunde()
        ▼
3. KundeWriteService.update()
        │ ├─ Kunde aus DB laden   → nicht gefunden → 404
        │ ├─ Version prüfen       → veraltet → 409
        │ ├─ Email prüfen         → existiert bei anderem → 422
        │ └─ kunde_db.set(kunde)  → Felder überschreiben
        ▼
4. KundeRepository.update()      ← session.add() + flush()
        │
        ▼
5. HTTP 204 No Content
   ETag: "1"                     ← neue Version
```

### DELETE

```shell
HTTP DELETE /rest/kunden/42
        │
        ▼
KundeWriteService.delete_by_id()
        │
        ▼
KundeRepository.delete_by_id()   ← lädt Kunde, dann session.delete()
        │                           cascade löscht Adresse + Bestellungen
        ▼
HTTP 204 No Content
```

---

## 2. Pydantic-Modelle (Eingabe-Validierung)

Pydantic-Modelle sind der „Türsteher" des Systems. Sie stehen zwischen dem HTTP-Request
und dem eigentlichen Code. Wenn der Request-Body nicht dem Schema entspricht,
gibt FastAPI automatisch HTTP 422 Unprocessable Entity zurück – noch bevor der Router-Code läuft.

---

### 2.1 [`router/adresse_model.py`](../../src/kunde/router/adresse_model.py)

```python
"""Pydantic-Model für die Adresse eines Kunden."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from kunde.entity import Adresse

__all__ = ["AdresseModel"]


class AdresseModel(BaseModel):
    strasse: Annotated[str, StringConstraints(max_length=64)]
    hausnummer: Annotated[str, StringConstraints(max_length=10)]
    plz: Annotated[str, StringConstraints(pattern=r"^\d{5}$")]
    ort: Annotated[str, StringConstraints(max_length=64)]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strasse": "Hauptstraße",
                "hausnummer": "12",
                "plz": "76133",
                "ort": "Karlsruhe",
            },
        }
    )

    def to_adresse(self) -> Adresse:
        adresse_dict = self.model_dump()
        adresse_dict["id"] = None
        adresse_dict["kunde_id"] = None
        adresse_dict["kunde"] = None
        return Adresse(**adresse_dict)
```

**`class AdresseModel(BaseModel)`**
Erbt von Pydantics `BaseModel`. Dadurch werden alle Felder automatisch validiert,
sobald das Objekt aus JSON erzeugt wird. Kein manuelles Validierungscode nötig.

**`Annotated[str, StringConstraints(max_length=64)]`**
`Annotated[Typ, Metadaten]` ist Standard-Python für Typ mit Zusatzinformationen.
`StringConstraints` ist Pydantic-spezifisch und erlaubt Einschränkungen:

- `max_length=64` → maximale Länge des Strings
- `max_length=10` → Hausnummern dürfen maximal 10 Zeichen haben
- `pattern=r"^\d{5}$"` → PLZ muss exakt 5 Ziffern sein (Regex)

**`^\d{5}$` im Detail:**

- `^` → Anfang des Strings
- `\d{5}` → genau 5 Ziffern (0-9)
- `$` → Ende des Strings
- `"76133"` passt, `"7613"` oder `"761334"` oder `"76abc"` schlagen fehl

**`model_config = ConfigDict(json_schema_extra={"example": {...}})`**
Definiert ein Beispiel-Objekt für die automatische API-Dokumentation (Swagger UI unter `/docs`).
Der Nutzer sieht dort direkt, wie ein gültiger Request-Body aussehen soll.

**`def to_adresse(self) -> Adresse:`**
Konvertiert das Pydantic-Modell in eine SQLAlchemy-Entity.

```python
adresse_dict = self.model_dump()
```

`model_dump()` serialisiert das Pydantic-Modell in ein normales Python-Dictionary:

```python
{"strasse": "Hauptstraße", "hausnummer": "12", "plz": "76133", "ort": "Karlsruhe"}
```

```python
adresse_dict["id"] = None
adresse_dict["kunde_id"] = None
adresse_dict["kunde"] = None
```

Die `Adresse`-Entity erwartet im Konstruktor auch `id`, `kunde_id` und `kunde`.
Da die Adresse neu angelegt wird, sind diese noch nicht bekannt → `None`.

```python
return Adresse(**adresse_dict)
```

`**adresse_dict` entpackt das Dictionary als Keyword-Argumente:

```python
# äquivalent zu:
Adresse(strasse="Hauptstraße", hausnummer="12", plz="76133", ort="Karlsruhe",
        id=None, kunde_id=None, kunde=None)
```

---

### 2.2 [`router/kunde_model.py`](../../src/kunde/router/kunde_model.py)

```python
"""Pydantic-Model für Kundendaten."""

from typing import Final

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr

from kunde.entity import Kunde
from kunde.router.adresse_model import AdresseModel

__all__ = ["KundeModel"]


class KundeModel(BaseModel):
    nachname: str
    email: EmailStr
    adresse: AdresseModel

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nachname": "Müller",
                "email": "mueller@example.de",
                "adresse": {
                    "strasse": "Hauptstraße",
                    "hausnummer": "12",
                    "plz": "76133",
                    "ort": "Karlsruhe",
                },
            },
        }
    )

    def to_kunde(self) -> Kunde:
        logger.debug("self={}", self)

        adresse = self.adresse.to_adresse()

        kunde: Final = Kunde(
            id=None,
            nachname=self.nachname,
            email=str(self.email),
            adresse=adresse,
            bestellungen=[],
        )

        logger.debug("kunde={}", kunde)
        return kunde
```

**`email: EmailStr`**
`EmailStr` ist ein spezieller Pydantic-Typ, der E-Mail-Adressen validiert.
`"keineemail"` schlägt fehl. `"mueller@example.de"` wird akzeptiert.
Intern prüft Pydantic das Format mit einer Regex.

**`adresse: AdresseModel`**
Hier ist das Feld selbst wieder ein Pydantic-Modell (`AdresseModel`).
Pydantic erkennt das und validiert das verschachtelte Objekt rekursiv.
Wenn `plz` im adresse-Objekt ungültig ist, schlägt die Validierung des ganzen `KundeModel` fehl.

**`def to_kunde(self) -> Kunde:`**

```python
adresse = self.adresse.to_adresse()
```

Erst die Adresse konvertieren (via `AdresseModel.to_adresse()`).

```python
kunde: Final = Kunde(
    id=None,
    nachname=self.nachname,
    email=str(self.email),
    adresse=adresse,
    bestellungen=[],
)
```

- `id=None` → noch keine Datenbankzeile, ID wird erst nach `flush()` vergeben
- `str(self.email)` → `EmailStr` ist intern ein spezieller Pydantic-Typ, muss zu `str` konvertiert werden
- `bestellungen=[]` → neuer Kunde startet ohne Bestellungen

---

### 2.3 [`router/kunde_update_model.py`](../../src/kunde/router/kunde_update_model.py)

```python
"""Pydantic-Model zum Aktualisieren von Kundedaten."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr

from kunde.entity import Kunde

__all__ = ["KundeUpdateModel"]


class KundeUpdateModel(BaseModel):
    nachname: str
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nachname": "Test",
                "email": "test@acme.com",
            },
        }
    )

    def to_dict(self) -> dict[str, Any]:
        kunde_dict = self.model_dump()
        kunde_dict["id"] = None
        kunde_dict["adresse"] = None
        kunde_dict["bestellungen"] = []
        return kunde_dict

    def to_kunde(self) -> Kunde:
        logger.debug("self={}", self)
        kunde_dict = self.to_dict()
        kunde = Kunde(**kunde_dict)
        logger.debug("kunde={}", kunde)
        return kunde
```

**Warum gibt es `KundeUpdateModel` statt `KundeModel` zu verwenden?**
Beim Update werden nur `nachname` und `email` geändert – nicht die Adresse und nicht die Bestellungen.
Ein separates Update-Modell macht den Request-Body kleiner und verhindert versehentliche Änderungen
an Feldern, die nicht verändert werden sollen.

**`def to_dict(self) -> dict[str, Any]:`**

```python
kunde_dict = self.model_dump()
# → {"nachname": "Test", "email": "test@acme.com"}

kunde_dict["id"] = None
kunde_dict["adresse"] = None
kunde_dict["bestellungen"] = []
```

Die `Kunde`-Entity hat mehr Felder als das Update-Modell.
`to_dict()` ergänzt die fehlenden Felder mit Platzhaltern, damit `Kunde(**kunde_dict)` funktioniert.

**Warum `adresse=None` beim Update-Objekt?**
Das Update-Objekt ist ein temporäres Objekt – nur die primitiven Felder werden danach
per `kunde_db.set(kunde)` in den geladenen Datenbank-Kunden kopiert.
`adresse` und `bestellungen` werden dabei nicht berührt, die bleiben im geladenen `kunde_db` erhalten.

---

## 3. Write-Service

### 3.1 [`service/kunde_write_service.py`](../../src/kunde/service/kunde_write_service.py)

```python
"""Geschäftslogik zum Schreiben von Kundendaten."""

from typing import Final

from loguru import logger

from kunde.entity import Kunde
from kunde.repository import KundeRepository, Session
from kunde.service.exceptions import (
    EmailExistsError,
    NotFoundError,
    VersionOutdatedError,
)
from kunde.service.kunde_dto import KundeDTO

__all__ = ["KundeWriteService"]


class KundeWriteService:
    def __init__(self, repo: KundeRepository) -> None:
        self.repo: KundeRepository = repo
```

Gleiche Dependency-Injection wie im `KundeReadService` –
das Repository kommt von außen, nicht vom Service selbst erstellt.

---

#### [`create`](../../src/kunde/service/kunde_write_service.py#L29)

```python
def create(self, kunde: Kunde) -> KundeDTO:
    email: Final = kunde.email

    with Session() as session:
        if self.repo.exists_email(email=email, session=session):
            raise EmailExistsError(email=email)

        kunde_db: Final = self.repo.create(
            kunde=kunde,
            session=session,
        )
        kunde_dto: Final = KundeDTO.from_kunde(kunde_db)

        session.commit()

    return kunde_dto
```

**`if self.repo.exists_email(email=email, session=session):`**
Vor dem Anlegen wird geprüft, ob die Email bereits vergeben ist.
Das ist **Geschäftslogik** – gehört nicht ins Repository (das kennt nur SQL)
und nicht in den Router (der kennt nur HTTP).

**`raise EmailExistsError(email=email)`**
Wenn die Email bereits existiert, wird eine Exception geworfen.
In `fastapi_app.py` ist ein Handler registriert:

```python
@app.exception_handler(EmailExistsError)
def email_exists_error_handler(...) -> Response:
    return create_problem_details(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, ...)
```

→ Der Nutzer bekommt HTTP 422.

**`kunde_db: Final = self.repo.create(kunde=kunde, session=session)`**
Das Repository speichert den Kunden und gibt ihn mit generierter ID zurück
(nach `session.flush()` hat `kunde_db.id` einen Wert).

**`KundeDTO.from_kunde(kunde_db)`**
Konvertiert die Entity in ein DTO – so gibt der Service nie eine SQLAlchemy-Entity zurück.

**`session.commit()`**
Erst nach erfolgreicher DTO-Konvertierung wird committed.
Wenn dabei etwas schiefgeht (z.B. DB-Constraint verletzt), wird automatisch rollback gemacht.

---

#### [`update`](../../src/kunde/service/kunde_write_service.py#L61)

```python
def update(self, kunde: Kunde, kunde_id: int, version: int) -> KundeDTO:
    with Session() as session:
        if (
            kunde_db := self.repo.find_by_id(
                kunde_id=kunde_id,
                session=session,
            )
        ) is None:
            raise NotFoundError(kunde_id)

        if kunde_db.version > version:
            raise VersionOutdatedError(version)

        email: Final = kunde.email
        if email != kunde_db.email and self.repo.exists_email_other_id(
            kunde_id=kunde_id,
            email=email,
            session=session,
        ):
            raise EmailExistsError(email)

        kunde_db.set(kunde)

        if (
            kunde_updated := self.repo.update(
                kunde=kunde_db,
                session=session,
            )
        ) is None:
            raise NotFoundError(kunde_id)

        kunde_dto: Final = KundeDTO.from_kunde(kunde_updated)

        session.commit()

        # Version erst nach Commit sichtbar
        kunde_dto.version += 1

        return kunde_dto
```

##### Schritt 1: Laden

```python
if (
    kunde_db := self.repo.find_by_id(kunde_id=kunde_id, session=session)
) is None:
    raise NotFoundError(kunde_id)
```

Walrus-Operator: lädt und prüft gleichzeitig. Wenn der Kunde nicht existiert → 404.

##### Schritt 2: Versionscheck (Optimistische Nebenläufigkeit)

```python
if kunde_db.version > version:
    raise VersionOutdatedError(version)
```

`version` kommt aus dem `If-Match`-Header des Requests.
`kunde_db.version` ist die aktuelle Version in der DB.

Szenario:

- User A und User B laden denselben Kunden (Version 0).
- User A speichert → DB-Version wird 1.
- User B versucht zu speichern mit `If-Match: "0"` → `0 < 1` → `VersionOutdatedError` → HTTP 409 Conflict.

User B muss erst neu laden und den Konflikt auflösen.

##### Schritt 3: Email-Uniqueness

```python
if email != kunde_db.email and self.repo.exists_email_other_id(
    kunde_id=kunde_id,
    email=email,
    session=session,
):
    raise EmailExistsError(email)
```

Nur prüfen wenn die Email sich geändert hat (`email != kunde_db.email`).
`exists_email_other_id` schließt den aktuellen Kunden aus – er darf seine eigene
Email „neu setzen" ohne Fehler.

##### Schritt 4: Felder überschreiben

```python
kunde_db.set(kunde)
```

`set()` ist eine Methode der `Kunde`-Entity:

```python
def set(self, kunde: Self) -> None:
    self.nachname = kunde.nachname
    self.email = kunde.email
```

Kopiert nur die primitiven Felder. Adresse und Bestellungen bleiben unverändert,
weil SQLAlchemy `kunde_db` noch in der Session hat.

##### Schritt 5: Speichern

```python
if (
    kunde_updated := self.repo.update(kunde=kunde_db, session=session)
) is None:
    raise NotFoundError(kunde_id)
```

Das Repository führt `session.add()` + `session.flush()` aus.
Wenn das Update fehlschlägt → erneut `NotFoundError`.

##### Schritt 6: Version manuell erhöhen

```python
session.commit()
kunde_dto.version += 1
```

Nach `commit()` erhöht die Datenbank intern die Version.
Das DTO wurde aber **vor** dem commit erstellt, deshalb wird `version`
manuell um 1 erhöht, damit der zurückgegebene ETag-Header stimmt.

---

#### [`delete_by_id`](../../src/kunde/service/kunde_write_service.py#L115)

```python
def delete_by_id(self, kunde_id: int) -> None:
    with Session() as session:
        self.repo.delete_by_id(
            kunde_id=kunde_id,
            session=session,
        )
        session.commit()
```

Der einfachste Fall: Session öffnen, Repository aufrufen, committen.
Wenn der Kunde nicht existiert, tut `delete_by_id` im Repository nichts (kein Fehler).
Das ist bewusstes Design: `DELETE` auf eine nicht-existierende Ressource ist idempotent.

---

## 4. Write-Router

### 4.1 [`router/kunde_write_router.py`](../../src/kunde/router/kunde_write_router.py)

```python
"""KundeWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from kunde.problem_details import create_problem_details
from kunde.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from kunde.router.dependencies import get_write_service
from kunde.router.kunde_model import KundeModel
from kunde.router.kunde_update_model import KundeUpdateModel
from kunde.service.kunde_write_service import KundeWriteService

__all__ = ["kunde_write_router"]

kunde_write_router: Final = APIRouter(tags=["Schreiben"])
```

**`tags=["Schreiben"]`** → separate Gruppe in der Swagger-Dokumentation,
getrennt von `tags=["Lesen"]` im Read-Router.

---

#### [`post`](../../src/kunde/router/kunde_write_router.py#L22) – neuen Kunden anlegen

```python
@kunde_write_router.post("")
def post(
    kunde_model: KundeModel,
    request: Request,
    service: Annotated[KundeWriteService, Depends(get_write_service)],
) -> Response:
    logger.debug("kunde_model={}", kunde_model)
    kunde_dto: Final = service.create(kunde=kunde_model.to_kunde())
    logger.debug("kunde_dto={}", kunde_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{kunde_dto.id}"},
    )
```

**`kunde_model: KundeModel`**
FastAPI erkennt automatisch, dass `KundeModel` ein Pydantic-Modell ist.
Es liest den Request-Body als JSON ein und validiert ihn gegen das Schema.
Ist der Body ungültig (fehlende Felder, falsche PLZ usw.) → HTTP 422 automatisch.

**`service.create(kunde=kunde_model.to_kunde())`**
Konvertierungskette: `JSON → KundeModel (Pydantic) → Kunde (SQLAlchemy-Entity) → KundeDTO (Service-Rückgabe)`

**`return Response(status_code=status.HTTP_201_CREATED, headers={"Location": ...})`**
HTTP 201 Created ist der Standard-Statuscode für erfolgreiches Anlegen einer Ressource.
Der `Location`-Header zeigt, unter welcher URL der neue Kunde abrufbar ist:

```shell
Location: http://localhost:8000/rest/kunden/42
```

`request.url` enthält die aktuelle URL (`/rest/kunden`), `kunde_dto.id` die neue ID.

---

#### [`put`](../../src/kunde/router/kunde_write_router.py#L49) – Kunden aktualisieren

```python
@kunde_write_router.put("/{kunde_id}")
def put(
    kunde_id: int,
    kunde_update_model: KundeUpdateModel,
    request: Request,
    service: Annotated[KundeWriteService, Depends(get_write_service)],
) -> Response:
    if_match_value: Final = request.headers.get(IF_MATCH)

    if if_match_value is None:
        return create_problem_details(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        )

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return create_problem_details(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)

    kunde: Final = kunde_update_model.to_kunde()
    kunde_modified: Final = service.update(
        kunde=kunde,
        kunde_id=kunde_id,
        version=version_int,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{kunde_modified.version}"'},
    )
```

**`if_match_value: Final = request.headers.get(IF_MATCH)`**
Liest den `If-Match`-Header aus dem Request. Dieser muss die aktuelle Version enthalten.
(`IF_MATCH = "if-match"` aus `constants.py`)

**Drei Validierungsschritte für den Header:**

1. **Fehlt der Header?**

   ```python
   if if_match_value is None:
       return create_problem_details(status_code=status.HTTP_428_PRECONDITION_REQUIRED)
   ```

   HTTP 428 Precondition Required: „Du musst einen `If-Match`-Header schicken."

2. **Hat der Wert das richtige Format?**

   ```python
   if (
       len(if_match_value) < IF_MATCH_MIN_LEN     # mindestens '"0"' = 3 Zeichen
       or not if_match_value.startswith('"')
       or not if_match_value.endswith('"')
   ):
       return create_problem_details(status_code=status.HTTP_412_PRECONDITION_FAILED)
   ```

   HTTP 412 Precondition Failed: Der Header-Wert ist syntaktisch falsch.
   Gültiges Format: `"0"`, `"42"`, `"100"` – immer in Anführungszeichen.

3. **Ist der Wert eine gültige Zahl?**

   ```python
   version: Final = if_match_value[1:-1]  # entfernt Anführungszeichen
   try:
       version_int: Final = int(version)
   except ValueError:
       return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)
   ```

   `if_match_value[1:-1]` schneidet das erste und letzte Zeichen ab:
   `'"42"'` → `'42'`. Dann `int("42")` → `42`.
   Wenn das fehlschlägt (z.B. `"abc"`), HTTP 412.

**`return Response(status_code=status.HTTP_204_NO_CONTENT, headers={"ETag": ...})`**
HTTP 204 No Content: Erfolg, kein Body.
Der neue `ETag`-Header enthält die neue Versionsnummer, damit der Client seinen Cache aktualisieren kann.

---

#### [`delete_by_id`](../../src/kunde/router/kunde_write_router.py#L107) – Kunden löschen

```python
@kunde_write_router.delete("/{kunde_id}")
def delete_by_id(
    kunde_id: int,
    service: Annotated[KundeWriteService, Depends(get_write_service)],
) -> Response:
    logger.debug("kunde_id={}", kunde_id)
    service.delete_by_id(kunde_id=kunde_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

Der einfachste aller Endpunkte:

1. `kunde_id` aus der URL lesen (FastAPI konvertiert automatisch zu `int`)
2. Service aufrufen
3. HTTP 204 No Content zurückgeben

Kein Body, kein Header außer dem Statuscode.
Wenn der Kunde nicht existiert, gibt es trotzdem 204 – DELETE ist idempotent.
(Mehrfaches Löschen der gleichen ID führt zum gleichen Ergebnis: die Ressource ist weg.)

---

## HTTP-Statuscodes Zusammenfassung

| Code | Name | Wann |
|------|------|------|
| 201 | Created | Neuer Kunde erfolgreich angelegt |
| 204 | No Content | Update oder Delete erfolgreich |
| 304 | Not Modified | ETag stimmt überein – Client nutzt Cache |
| 404 | Not Found | Kunde mit dieser ID existiert nicht |
| 409 | Conflict | Versionsnummer veraltet (`VersionOutdatedError`) |
| 412 | Precondition Failed | `If-Match`-Header syntaktisch falsch |
| 422 | Unprocessable Entity | Validierungsfehler (Pydantic) oder Email bereits vergeben |
| 428 | Precondition Required | `If-Match`-Header fehlt komplett |

---

## Zusammenfassung: Was macht jede Klasse?

| Klasse | Aufgabe |
|--------|---------|
| `AdresseModel` | Validiert Adress-JSON (Pydantic), konvertiert zu Entity |
| `KundeModel` | Validiert Kunden-JSON für POST (Pydantic), konvertiert zu Entity |
| `KundeUpdateModel` | Validiert Kunden-JSON für PUT (nur Name + Email), konvertiert zu Entity |
| `KundeWriteService` | Geschäftslogik: Email-Check, Version-Check, Session-Management |
| `KundeWriteRouter` | HTTP-Protokoll: Header lesen, Statuscodes setzen, Pydantic-Validierung auslösen |

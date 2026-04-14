# Code-Walkthrough: Kundenverwaltung

Reihenfolge: Entity → Repository → Service → Router → App

Disclaimer: Diese Erklärung ist von Claude Code generiert worden.

---

## Architektur

```text
HTTP Request → Router → Service → Repository → Entity → DB
```

Jede Schicht kennt nur die direkt darunter liegende. Der Router redet nie direkt mit dem Repository.

---

## Inhaltsverzeichnis

1. [Entity-Layer](#1-entity-layer)
2. [Repository-Layer](#2-repository-layer)
3. [Service-Layer](#3-service-layer)
4. [Router-Layer](#4-router-layer)
5. [App](#5-app)

---

## 1. Entity-Layer

Entities sind Python-Klassen, die direkt auf DB-Tabellen gemappt werden. Alle erben von `Base`.

### 1.1 `entity/base.py`

```python
from typing import TYPE_CHECKING, Any
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    class MappedAsDataclass:
        def __init__(self, *arg: Any, **kw: Any) -> None: ...
else:
    from sqlalchemy.orm import MappedAsDataclass

class Base(MappedAsDataclass, DeclarativeBase):
    """Basisklasse für alle Entity-Klassen."""
```

`DeclarativeBase` registriert alle Unterklassen im SQLAlchemy-ORM. `MappedAsDataclass` macht Entities automatisch zu Python-Dataclasses (Felder werden Konstruktor-Parameter, `__repr__` gratis).

Der `if TYPE_CHECKING`-Block ist ein IDE-Trick: `MappedAsDataclass` trägt PEP 681-Annotationen, die der Typprüfer zu streng interpretiert und Feldreihenfolgefehler meldet. Zur Typprüfzeit sieht der Prüfer nur den leeren Stub — zur Laufzeit greift der `else`-Zweig mit der echten Klasse.

### 1.2 `entity/__init__.py`

```python
from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung
from kunde.entity.kunde import Kunde

__all__ = ["Adresse", "Base", "Bestellung", "Kunde"]
```

`__all__` legt die öffentliche API fest und erlaubt `from kunde.entity import Kunde` statt des langen vollständigen Pfads.

### 1.3 `entity/adresse.py` — Vollständig erklärt

```python
from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship
from kunde.entity.base import Base

class Adresse(Base):
    __tablename__ = "adresse"

    strasse: Mapped[str]
    hausnummer: Mapped[str]
    plz: Mapped[str]
    ort: Mapped[str]

    id: Mapped[int] = mapped_column(Identity(start=1000), primary_key=True)
    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"), unique=True)
    kunde: Mapped[Kunde] = relationship(back_populates="adresse")
```

`__tablename__` legt den DB-Tabellennamen fest. `Mapped[str]` erzeugt eine NOT NULL VARCHAR-Spalte — kein `mapped_column(...)` nötig wenn keine Sonderoptionen gefragt sind. Felder ohne Default stehen oben (Dataclass-Pflicht).

`Identity(start=1000)` startet die Auto-Increment-Sequenz bei 1000 — IDs unter 1000 bleiben für feste Testdaten reserviert, um keine Kollision mit generierten IDs zu riskieren.

`ForeignKey("kunde.id")` erzeugt einen echten SQL-Fremdschlüssel: Die DB selbst erzwingt referentielle Integrität. `unique=True` begrenzt auf 1:1 — dieselbe `kunde_id` darf in der `adresse`-Tabelle nur einmal vorkommen.

`relationship(back_populates="adresse")` gibt Python-Zugriff auf das echte `Kunde`-Objekt statt nur auf die numerische `kunde_id`. `back_populates` hält beide Seiten synchron: `adresse.kunde = x` setzt automatisch auch `x.adresse = adresse`.

```python
    def __repr__(self) -> str:
        return f"Adresse(id={self.id}, strasse={self.strasse}, ...)"
```

`self.kunde` fehlt absichtlich: Zugriff darauf würde bei lazy-loaded Objekten automatisch eine SQL-Abfrage auslösen — unerwünscht beim Loggen.

### 1.4 `entity/bestellung.py` — Unterschiede zu Adresse

```python
class Bestellung(Base):
    __tablename__ = "bestellung"
    produktname: Mapped[str]
    menge: Mapped[int]
    id: Mapped[int] = mapped_column(Identity(start=1000), primary_key=True)
    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"))  # kein unique=True!
    kunde: Mapped[Kunde] = relationship(back_populates="bestellungen")
```

Identisches Muster wie `Adresse`. Einziger struktureller Unterschied: `kunde_id` hat kein `unique=True`. Das erlaubt dieselbe `kunde_id` mehrfach — damit ist die 1:N-Beziehung implementiert. `back_populates="bestellungen"` (Plural) spiegelt wider, dass `Kunde.bestellungen` eine Liste ist.

### 1.5 `entity/kunde.py` — Besonderheiten

```python
from typing import Any, Self

class Kunde(Base):
    __tablename__ = "kunde"
    nachname: Mapped[str]
    id: Mapped[int | None] = mapped_column(Identity(start=1000), primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    adresse: Mapped[Adresse] = relationship(
        back_populates="kunde", innerjoin=True, cascade="save-update, delete"
    )
    bestellungen: Mapped[list[Bestellung]] = relationship(
        back_populates="kunde", cascade="save-update, delete"
    )
    version: Mapped[int] = mapped_column(default=0)
```

`id: Mapped[int | None]` — vor dem Speichern hat das Objekt noch keine ID (vergibt die DB). `int | None` drückt diesen Zustand explizit aus.

`innerjoin=True` bei `adresse`: SQLAlchemy verwendet einen INNER JOIN statt LEFT OUTER JOIN — ein Kunde ohne Adresse liefert kein Ergebnis, was die 1:1-Pflicht erzwingt. Bei `bestellungen` fehlt das, weil ein Kunde ohne Bestellungen valid ist.

`cascade="save-update, delete"`: Beim Speichern des Kunden wird die Adresse mitgespeichert, beim Löschen mitgelöscht — kein manuelles Aufräumen nötig.

`version: Mapped[int] = mapped_column(default=0)` ermöglicht optimistische Nebenläufigkeitskontrolle: Der Client schickt beim Update die bekannte Version mit (`If-Match: "0"`), der Server prüft ob sie noch aktuell ist.

```python
    def set(self, kunde: Self) -> None:
        self.nachname = kunde.nachname
        self.email = kunde.email
```

`Self` (statt `Kunde`) vermeidet einen zirkulären Import und funktioniert korrekt bei Vererbung. `set()` kapselt die Update-Logik: Kommt ein neues Feld hinzu, wird nur diese Methode angepasst.

```python
    def __eq__(self, other: Any) -> bool:
        if self is other: return True
        if not isinstance(other, type(self)): return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id is not None else hash(type(self))
```

Zwei Kunden sind gleich wenn ihre IDs gleich sind. `self.id is not None` verhindert, dass zwei ungespeicherte Objekte (beide `id=None`) fälschlich als gleich gelten. `__hash__` muss bei überschriebenem `__eq__` immer mit definiert werden, damit Objekte in Sets und als Dict-Keys verwendet werden können.

---

## 2. Repository-Layer

Das Repository ist die **einzige Schicht die SQL-Abfragen baut**. Der Service weiß nicht, wie Daten gespeichert werden.

### 2.1 `repository/pageable.py`

```python
from __future__ import annotations
from dataclasses import dataclass

DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_NUMBER = 0

@dataclass(eq=False, slots=True, kw_only=True)
class Pageable:
    size: int
    number: int
```

`from __future__ import annotations` macht alle Typ-Annotationen zu lazy strings — `Pageable` kann im Rückgabetyp von `create()` stehen, bevor die Klasse vollständig definiert ist.

`slots=True` ersetzt `__dict__` durch feste Slots — spart RAM und beschleunigt Attributzugriff. `kw_only=True` erzwingt `Pageable(size=5, number=0)` statt `Pageable(5, 0)` — lesbarer. `eq=False` deaktiviert automatisches `__eq__`, da Pageable-Objekte nie verglichen werden.

```python
    @staticmethod
    def create(number: str | None = None, size: str | None = None) -> Pageable:
        number_int: Final = DEFAULT_PAGE_NUMBER if number is None or not number.isdigit() else int(number)
        size_int: Final = (
            DEFAULT_PAGE_SIZE if size is None or not size.isdigit()
            or int(size) > MAX_PAGE_SIZE or int(size) < 0 else int(size)
        )
        return Pageable(size=size_int, number=number_int)

    @property
    def offset(self) -> int:
        return self.number * self.size
```

Parameter sind `str | None` weil HTTP-Query-Parameter immer als Text ankommen. `isdigit()` ist schneller und sicherer als `try/except ValueError`. Die `offset`-Property berechnet `OFFSET` für SQL-Paginierung: Seite 2 mit Größe 5 → `offset = 10`.

### 2.2 `repository/slice.py`

```python
@dataclass(eq=False, slots=True, kw_only=True)
class Slice[T]:
    content: tuple[T, ...]
    total_elements: int
```

`Slice[T]` nutzt PEP 695-Syntax (Python 3.12) für generische Klassen. `tuple[T, ...]` statt Liste: Das Ergebnis soll nach dem Lesen unveränderlich sein. `total_elements` enthält die Gesamttreffer in der DB (unabhängig von der aktuellen Seite) — der Router braucht diese Zahl für `total_pages`.

### 2.3 `repository/kunde_repository.py`

#### `find_by_id` — vollständig erklärt

```python
def find_by_id(self, kunde_id: int | None, session: Session) -> Kunde | None:
    if kunde_id is None:
        return None

    statement: Final = (
        select(Kunde)
        .options(joinedload(Kunde.adresse), joinedload(Kunde.bestellungen))
        .where(Kunde.id == kunde_id)
    )
    return session.scalar(statement)
```

`int | None` als Parameter: Der Service übergibt IDs aus HTTP-Requests, die fehlen können. Die Methode behandelt `None` selbst — kein Prüfcode beim Aufrufer nötig.

`joinedload` erzeugt einen SQL-JOIN statt separater Folgeabfragen. Ohne `joinedload` würde SQLAlchemy bei jedem Zugriff auf `kunde.adresse` eine neue DB-Abfrage starten (N+1-Problem). `.where(Kunde.id == kunde_id)` ist kein Python-Vergleich, sondern ein überladener Operator — SQLAlchemy baut daraus `WHERE id = ?` als Prepared Statement (schützt vor SQL-Injection).

`session.scalar()` gibt genau ein Objekt zurück, oder `None` bei keinem Treffer.

#### `find` — Dispatcher-Muster

```python
def find(self, suchparameter: Mapping[str, str], pageable: Pageable, session: Session) -> Slice[Kunde]:
    if not suchparameter:
        return self._find_all(pageable=pageable, session=session)
    for key, value in suchparameter.items():
        if key == "email":
            kunde = self._find_by_email(email=value, session=session)
            return Slice(content=(kunde,), total_elements=1) if kunde else Slice(content=(), total_elements=0)
        if key == "nachname":
            return self._find_by_nachname(teil=value, pageable=pageable, session=session)
    return Slice(content=(), total_elements=0)
```

`find()` ist die einzige öffentliche Such-Methode — sie verteilt an private Methoden. `(kunde,)` ist ein Tupel mit einem Element (Komma zwingend). Unbekannte Suchparameter liefern ein leeres `Slice` statt einen Fehler.

#### `_find_all` — Paginierung

```python
def _find_all(self, pageable: Pageable, session: Session) -> Slice[Kunde]:
    statement = (
        select(Kunde).options(joinedload(Kunde.adresse), joinedload(Kunde.bestellungen))
        .limit(pageable.size).offset(pageable.offset)
    ) if pageable.size != 0 else select(Kunde).options(...)

    kunden = session.scalars(statement).unique().all()
    return Slice(content=tuple(kunden), total_elements=self._count_all_rows(session))
```

`.unique()` ist bei `joinedload` auf 1:N-Beziehungen **zwingend**: Ein JOIN erzeugt mehrere Zeilen pro Kunde (eine pro Bestellung). Ohne `.unique()` erscheint jeder Kunde mehrfach im Ergebnis. `_count_all_rows()` macht eine separate `SELECT COUNT(*)`-Abfrage für `total_elements`, da `LIMIT` die Gesamtzahl versteckt.

#### `find_nachnamen`, `exists_email`, `exists_email_other_id`

```python
def find_nachnamen(self, teil: str, session: Session) -> list[str]:
    statement = select(Kunde.nachname).where(Kunde.nachname.ilike(f"%{teil}%")).distinct()
    return list(session.scalars(statement))
```

`select(Kunde.nachname)` selektiert nur die Spalte, nicht das Objekt — Ergebnis ist `list[str]`. `ilike` ist case-insensitiver LIKE. `%` sind SQL-Wildcards. `.distinct()` verhindert doppelte Nachnamen.

```python
def exists_email(self, email: str, session: Session) -> bool:
    return (session.scalar(select(func.count()).where(Kunde.email == email)) or 0) > 0

def exists_email_other_id(self, kunde_id: int, email: str, session: Session) -> bool:
    # Gleiches Muster, zusätzlich: .where(Kunde.id != kunde_id)
    # Beim Update darf der Kunde seine eigene Email behalten
```

`COUNT(*)` ist effizienter als `SELECT *` — die DB muss keine Zeilen übertragen.

#### `create` und `delete_by_id`

```python
def create(self, kunde: Kunde, session: Session) -> Kunde:
    session.add(instance=kunde)
    session.flush(objects=[kunde])   # DB vergibt ID, noch kein commit
    return kunde
```

`flush()` schreibt in die DB innerhalb der laufenden Transaktion (noch kein `commit`). Der wichtige Effekt: Die DB vergibt die ID sofort — die kann danach direkt im Location-Header zurückgegeben werden.

```python
def delete_by_id(self, kunde_id: int, session: Session) -> None:
    kunde = self.find_by_id(kunde_id=kunde_id, session=session)
    if kunde is None:
        return   # kein Fehler — DELETE ist idempotent
    session.delete(kunde)
    session.flush()
```

SQLAlchemy muss das Objekt kennen bevor es gelöscht werden kann. `cascade="delete"` in der Entity sorgt dafür, dass Adresse und Bestellungen automatisch mitgelöscht werden.

---

## 3. Service-Layer

Der Service enthält die Geschäftslogik. Er ist der **einzige Ort der Sessions öffnet**. Nach außen gibt er nur DTOs zurück.

### 3.1 `service/exceptions.py`

```python
class EmailExistsError(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Existierende Email: {email}")
        self.email = email

class NotFoundError(Exception):
    def __init__(self, kunde_id: int | None = None, suchparameter: Mapping[str, str] | None = None) -> None:
        super().__init__("Not Found")

class VersionOutdatedError(Exception):
    def __init__(self, version: int) -> None:
        super().__init__(f"Veraltete Version: {version}")
```

Eigene Exception-Klassen erlauben gezieltes Fangen: `except EmailExistsError` trifft nur diesen Fehlertyp und ermöglicht die passende HTTP-Antwort. `str(err)` gibt die Nachricht aus `super().__init__(...)` zurück.

`NotFoundError` hat optionale Parameter (beide `= None`) weil er in drei Fällen geworfen wird: per ID, per Suchparameter, oder ohne Kontext.

### 3.2 DTOs — Muster einmal erklärt

DTO (Data Transfer Object) — eine einfache Datenklasse ohne DB-Logik. Grund: Die Entity enthält DB-interne Felder (`kunde_id`, `id`, Rückreferenz auf `Kunde`). Ein unvorsichtiger Zugriff darauf nach Schließen der Session würde eine SQL-Abfrage auslösen. Das DTO ist ein sauberer Schnitt.

```python
@dataclass(eq=False, slots=True, kw_only=True)
class AdresseDTO:
    plz: str
    ort: str   # nur fachlich relevante Felder, kein id / kunde_id

    @classmethod
    def from_adresse(cls, adresse: Adresse) -> "AdresseDTO":
        return cls(plz=adresse.plz, ort=adresse.ort)
```

`@classmethod` bekommt `cls` statt `self` — ermöglicht `cls(...)` statt `AdresseDTO(...)` direkt, was Vererbung vereinfacht. `"AdresseDTO"` in Anführungszeichen ist ein Forward Reference: Die Klasse ist im Rückgabetyp noch nicht vollständig definiert.

`BestellungDTO` ist strukturell identisch: selbe `@dataclass`-Optionen, selbe `from_bestellung()`-Factory. Felder: `produktname: str`, `menge: int`.

### 3.3 `service/kunde_dto.py`

```python
from __future__ import annotations

@dataclass
class KundeDTO:
    id: int | None
    nachname: str
    email: str
    version: int
    adresse: AdresseDTO
    bestellungen: list[BestellungDTO]

    @classmethod
    def from_kunde(cls, kunde: Kunde) -> KundeDTO:
        return cls(
            id=kunde.id, nachname=kunde.nachname, email=kunde.email, version=kunde.version,
            adresse=AdresseDTO.from_adresse(kunde.adresse),
            bestellungen=[BestellungDTO.from_bestellung(b) for b in kunde.bestellungen],
        )
```

`from __future__ import annotations` ersetzt Forward References in Anführungszeichen. Die List Comprehension `[BestellungDTO.from_bestellung(b) for b in ...]` konvertiert alle Bestellungen. Jedes DTO ist für seine eigene Konvertierung zuständig — `KundeDTO.from_kunde` delegiert weiter.

### 3.4 `service/kunde_read_service.py`

```python
class KundeReadService:
    def __init__(self, repo: KundeRepository) -> None:
        self.repo = repo
```

Dependency Injection: Der Service erstellt das Repository nicht selbst — es wird übergeben. Für Tests kann man ein Mock-Repository einsetzen ohne echte DB.

#### `find_by_id` — Session und Walrus-Operator

```python
def find_by_id(self, kunde_id: int) -> KundeDTO:
    with Session() as session:
        if (kunde := self.repo.find_by_id(kunde_id=kunde_id, session=session)) is None:
            raise NotFoundError(kunde_id=kunde_id)
        kunde_dto: Final = KundeDTO.from_kunde(kunde)
        session.commit()
    return kunde_dto
```

`with Session() as session:` öffnet eine DB-Verbindung inklusive Transaktion. `__exit__` schließt sie automatisch — auch bei Exceptions.

`:=` ist der Walrus-Operator (Python 3.8): Zuweisung und Prüfung in einem Ausdruck. `if (x := f()) is None` ersetzt zwei Zeilen: `x = f(); if x is None`.

`KundeDTO.from_kunde(kunde)` muss **innerhalb** des `with`-Blocks passieren: Zugriff auf `kunde.adresse` und `kunde.bestellungen` braucht eine offene Session (auch wenn `joinedload` sie bereits geladen hat). Nach dem `with`-Block hat das DTO nur Python-Objekte — keine DB-Verbindung nötig.

`session.commit()` bei Leseoperationen ist Best Practice: Es signalisiert der DB, dass die Transaktion abgeschlossen ist und Sperren freigegeben werden können.

#### `find` und `find_nachnamen`

```python
def find(self, suchparameter, pageable) -> Slice[KundeDTO]:
    with Session() as session:
        kunde_slice = self.repo.find(suchparameter=suchparameter, pageable=pageable, session=session)
        if len(kunde_slice.content) == 0:
            raise NotFoundError(suchparameter=suchparameter)
        kunden_dto: Final = tuple(KundeDTO.from_kunde(k) for k in kunde_slice.content)
        session.commit()
    return Slice(content=kunden_dto, total_elements=kunde_slice.total_elements)
```

`tuple(... for ...)` ist ein Generator-Ausdruck: Keine Zwischenliste im RAM — direkt als Tupel materialisiert. Das `Slice` wird **außerhalb** des `with`-Blocks erstellt, weil `kunden_dto` nur Python-Objekte enthält.

`find_nachnamen` folgt demselben Session-Muster. `raise NotFoundError` ohne Argumente ist möglich, weil beide Parameter `= None` haben.

---

## 4. Router-Layer

Der Router empfängt HTTP-Requests, ruft den Service auf und gibt HTTP-Antworten zurück. **Keine Geschäftslogik** — nur HTTP-Protokoll.

### 4.1 `router/constants.py`

```python
ETAG: Final = "ETag"
IF_MATCH: Final = "if-match"
IF_NONE_MATCH: Final = "If-None-Match"
IF_NONE_MATCH_MIN_LEN: Final = 3   # '"0"' hat Länge 3
```

Magic Strings als benannte Konstanten: Tippfehler in `ETAG` werden sofort als `NameError` erkannt; ein falsch geschriebener String-Literal `"ETags"` wird stillschweigend akzeptiert. `MIN_LEN = 3` entspricht dem kürzest möglichen ETag: `"0"` (Anführungszeichen + Ziffer + Anführungszeichen).

ETag ist ein HTTP-Caching-Mechanismus: Server schickt `ETag: "0"`, Client schickt es beim nächsten Request als `If-None-Match: "0"` zurück, Server antwortet mit 304 wenn unverändert.

### 4.2 `router/page.py`

```python
@dataclass
class Page:
    content: tuple[dict[str, Any], ...]
    page_number: int
    page_size: int
    total_elements: int
    total_pages: int

    @classmethod
    def create(cls, content, pageable, total_elements) -> "Page":
        total_pages = max(1, (total_elements + pageable.size - 1) // pageable.size)
        return cls(content=content, page_number=pageable.number, ...)
```

`Slice` enthält Python-Objekte (DTOs), `Page` enthält JSON-kompatible Dictionaries plus Paginierungsmetadaten. `(n + size - 1) // size` ist die Standard-Formel für Aufrunden mit ganzzahliger Division: 14 Einträge, 5 pro Seite → `(14+4)//5 = 3`. `max(1, ...)` verhindert `total_pages = 0` bei leerer DB.

### 4.3 `router/kunde_read_router.py`

```python
kunde_read_router: Final = APIRouter(tags=["Lesen"])
```

`APIRouter` gruppiert Routen — in `fastapi_app.py` eingebunden mit `prefix="/rest/kunden"`. `tags=["Lesen"]` gruppiert Endpunkte in Swagger.

#### `get_by_id`

```python
@kunde_read_router.get("/{kunde_id}")
def get_by_id(
    kunde_id: int,
    request: Request,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> Response:
```

`/{kunde_id}` → FastAPI extrahiert den Pfadparameter und konvertiert ihn zu `int`. Ungültige Eingabe (z.B. `/abc`) ergibt automatisch HTTP 422.

`Annotated[KundeReadService, Depends(get_read_service)]` ist FastAPIs Dependency Injection: `get_read_service()` wird von FastAPI aufgerufen, das Ergebnis als `service` übergeben.

```python
    if_none_match = request.headers.get(IF_NONE_MATCH)
    if if_none_match and len(if_none_match) >= 3 and if_none_match.startswith('"') and if_none_match.endswith('"'):
        try:
            if int(if_none_match[1:-1]) == kunde.version:
                return Response(status_code=status.HTTP_304_NOT_MODIFIED)
        except ValueError:
            pass  # ungültiger ETag → regulärer 200

    return JSONResponse(content=_kunde_to_dict(kunde), headers={ETAG: f'"{kunde.version}"'})
```

`if_none_match[1:-1]` schneidet Anführungszeichen ab: `'"42"'` → `'42'`. Bei übereinstimmender Version: 304 ohne Body — spart Bandbreite. Ansonsten: JSON-Antwort mit neuem ETag-Header.

#### `get` — Query-Parameter

```python
@kunde_read_router.get("")
def get(request: Request, service: ...) -> JSONResponse:
    query_params = request.query_params
    pageable = Pageable.create(number=query_params.get("page"), size=query_params.get("size"))
    suchparameter = dict(query_params)
    suchparameter.pop("page", None)   # zweites Argument verhindert KeyError
    suchparameter.pop("size", None)
    return JSONResponse(content=_kunde_slice_to_page(service.find(suchparameter, pageable), pageable))
```

`dict(query_params)` erzeugt eine veränderliche Kopie (Original ist unveränderlich, `pop()` nicht möglich). `page` und `size` werden entfernt — das Repository würde nicht wissen was mit `key="page"` anzufangen ist.

#### `get_nachnamen` und Hilfsfunktionen

```python
@kunde_read_router.get("/nachnamen/{teil}")
def get_nachnamen(teil: str, service: ...) -> JSONResponse:
    return JSONResponse(content=service.find_nachnamen(teil=teil))
```

Einfachster Endpunkt: Teilstring aus URL → Service → JSON. `list[str]` ist direkt JSON-serialisierbar.

```python
def _kunde_to_dict(kunde: KundeDTO) -> dict[str, Any]:
    return {"id": kunde.id, "nachname": kunde.nachname, "email": kunde.email,
            "adresse": {"plz": kunde.adresse.plz, "ort": kunde.adresse.ort},
            "bestellungen": [{"produktname": b.produktname, "menge": b.menge} for b in kunde.bestellungen]}
```

`_kunde_to_dict` (führender `_` = privat) kontrolliert **exakt** welche Felder in der JSON-Antwort erscheinen. `asdict(obj=page)` in `_kunde_slice_to_page` konvertiert das `Page`-Dataclass rekursiv zum Dictionary.

---

## 5. App

### 5.1 `fastapi_app.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    if dev_db_populate:
        db_populate()
    banner(app.routes)
    yield                       # ← Server läuft zwischen Start und Shutdown
    engine.dispose()            # Datenbankverbindungen sauber schließen

app: Final = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=500)
```

`lifespan` ist ein async Context Manager: alles vor `yield` läuft beim Start, alles danach beim Shutdown. `GZipMiddleware` komprimiert Antworten ab 500 Bytes — kleinere würden durch den GZip-Header selbst größer werden.

```python
@app.middleware("http")
async def log_request(request: Request, call_next: Callable) -> Response:
    logger.debug(f"{request.method} '{request.url}'")
    return await call_next(request)   # gibt an nächste Middleware/Handler weiter

@app.middleware("http")
async def log_response_time(request: Request, call_next: Callable) -> Response:
    start = time()
    response = await call_next(request)
    logger.debug(f"Response time: {(time()-start)*1000:.2f} ms")
    return response
```

Jeder Request durchläuft beide Middlewares. `await` ist nötig weil FastAPI asynchron arbeitet.

```python
app.include_router(kunde_read_router, prefix="/rest/kunden")
app.include_router(kunde_write_router, prefix="/rest")
if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")
```

`include_router` setzt den Präfix vor alle Routen des Routers: `get("/{id}")` + `prefix="/rest/kunden"` → `GET /rest/kunden/{id}`. Der Dev-Router ist in Produktion **nicht registriert** — die Endpunkte zum DB-Befüllen sind schlicht nicht erreichbar.

```python
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request, _err) -> Response:
    return create_problem_details(status_code=status.HTTP_404_NOT_FOUND)

@app.exception_handler(EmailExistsError)
def email_exists_error_handler(_request, err: EmailExistsError) -> Response:
    return create_problem_details(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
```

FastAPI fängt geworfene Exceptions automatisch ab — kein `try/except` in jedem Handler nötig. `_request` / `_err` (führender Unterstrich) signalisiert unbenutzte Parameter. `str(err)` liefert die Meldung aus `super().__init__(...)`.

`create_problem_details` erzeugt RFC 7807-konforme Fehlerantworten: Ein JSON-Objekt mit `type`, `title`, `status` und optionalem `detail`.

---

## Datenfluss: GET /rest/kunden/1

```text
HTTP GET /rest/kunden/1
  → get_by_id(kunde_id=1)                      Router
  → KundeReadService.find_by_id(1)              Service öffnet Session
  → KundeRepository.find_by_id(1, session)      Repository baut SQL
  → SELECT * FROM kunde JOIN adresse JOIN bestellung WHERE id = 1
  → Kunde-Entity (SQLAlchemy-Objekt)
  → KundeDTO.from_kunde(kunde)                  Service konvertiert, Session schließt
  → _kunde_to_dict(kunde_dto)                   Router serialisiert
  → JSONResponse mit ETag: "0"                  HTTP Response
```

---

Leon Jungkind

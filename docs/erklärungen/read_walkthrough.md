# Code-Walkthrough: Kundenverwaltung

Dieses Dokument erklärt jede Datei des Projekts Zeile für Zeile.
Reihenfolge: **Entity → Repository → Service → Router → App**

**Disclaimer: Diese Erklärung ist von Claude Code Generiert worden!**

---

## Inhaltsverzeichnis

1. [Entity-Layer](#1-entity-layer)
   - [base.py](#11-entitybasepy)
   - [\_\_init\_\_.py](#12-entity__init__py)
   - [adresse.py](#13-entityadressepy)
   - [bestellung.py](#14-entitybestellungpy)
   - [kunde.py](#15-entitykundepy)
2. [Repository-Layer](#2-repository-layer)
   - [pageable.py](#21-repositorypageablepy)
   - [slice.py](#22-repositoryslicepy)
   - [kunde\_repository.py](#23-repositorykunde_repositorypy)
3. [Service-Layer](#3-service-layer)
   - [exceptions.py](#31-serviceexceptionspy)
   - [adresse\_dto.py](#32-serviceadresse_dtopy)
   - [bestellung\_dto.py](#33-servicebestellung_dtopy)
   - [kunde\_dto.py](#34-servicekunde_dtopy)
   - [kunde\_read\_service.py](#35-servicekunde_read_servicepy)
4. [Router-Layer](#4-router-layer)
   - [constants.py](#41-routerconstantspy)
   - [page.py](#42-routerpagepy)
   - [kunde\_read\_router.py](#43-routerkunde_read_routerpy)
5. [App](#5-app)
   - [fastapi\_app.py](#51-fastapi_apppy)

---

## Architektur-Überblick

```text
HTTP Request
    │
    ▼
┌─────────────┐
│   Router    │  empfängt HTTP, validiert Parameter, gibt HTTP zurück
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │  Geschäftslogik, wirft Exceptions bei Fehlern
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repository  │  SQL-Abfragen, kennt nur Entities
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Entity    │  Python-Klassen, die DB-Tabellen abbilden
└─────────────┘
```

Jede Schicht kennt nur die direkt darunter liegende. Der Router redet nie direkt mit dem Repository.

---

## 1. Entity-Layer

Entities sind Python-Klassen, die direkt auf Datenbanktabellen gemappt werden.
Sie erben alle von `Base` und sind gleichzeitig SQLAlchemy-ORM-Objekte und Python-Dataclasses.

---

### 1.1 [`entity/base.py`](../../src/kunde/entity/base.py)

```python
from typing import TYPE_CHECKING, Any
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    class MappedAsDataclass:
        def __init__(self, *arg: Any, **kw: Any) -> None: ...
else:
    from sqlalchemy.orm import MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    """Basisklasse für Entity-Klassen als dataclass."""
```

**`TYPE_CHECKING`** ist eine Konstante aus `typing`, die zur Laufzeit immer `False` ist.
Sie wird nur `True`, wenn ein statischer Typprüfer (Pylance, mypy) die Datei analysiert.

**Warum der `if TYPE_CHECKING`-Block?**
`MappedAsDataclass` aus SQLAlchemy trägt PEP 681-Annotationen, die der IDE sagen:
„Behandle Unterklassen wie Dataclasses – Felder mit Default müssen nach Felder ohne Default kommen."
Das ist manchmal zu streng. Deshalb ersetzt man die echte Klasse zur **Typprüfzeit** durch einen
harmlosen leeren Stub. Zur **Laufzeit** (`else`-Zweig) wird das echte `MappedAsDataclass` geladen.

**`DeclarativeBase`** ist die SQLAlchemy-Basisklasse: Jede Klasse, die davon erbt,
wird automatisch im ORM-Registry registriert und zur Datenbanktabelle gemappt.

**`class Base(MappedAsDataclass, DeclarativeBase)`**
Kombiniert beide Mixins in einer einzigen Basisklasse.
`Adresse`, `Bestellung` und `Kunde` erben von `Base` und bekommen dadurch beides gleichzeitig.

---

### 1.2 [`entity/__init__.py`](../../src/kunde/entity/__init__.py)

```python
"""Modul für persistente kundendaten."""

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung
from kunde.entity.kunde import Kunde

__all__ = [
    "Adresse",
    "Base",
    "Bestellung",
    "Kunde",
]
```

Die vier Imports holen alle Entity-Klassen in den Namensraum des `entity`-Pakets.

**`__all__`** definiert die öffentliche API des Moduls – was exportiert wird,
wenn jemand `from kunde.entity import *` schreibt. Es dient auch als Dokumentation.

**Praktischer Nutzen:** Statt `from kunde.entity.kunde import Kunde` reicht
`from kunde.entity import Kunde` – der Importpfad wird kürzer und übersichtlicher.

---

### 1.3 [`entity/adresse.py`](../../src/kunde/entity/adresse.py)

```python
"""Entity-Klasse für die Adresse."""

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.base import Base


class Adresse(Base):
    __tablename__ = "adresse"

    strasse: Mapped[str]
    hausnummer: Mapped[str]
    plz: Mapped[str]
    ort: Mapped[str]

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )

    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"), unique=True)

    kunde: Mapped[Kunde] = relationship(
        back_populates="adresse",
    )

    def __repr__(self) -> str:
        return (
            f"Adresse(id={self.id}, strasse={self.strasse}, "
            f"hausnummer={self.hausnummer}, plz={self.plz}, ort={self.ort})"
        )
```

**`__tablename__ = "adresse"`**
Gibt an, in welche Datenbanktabelle diese Klasse gemappt wird.

**`Mapped[str]`**
Typ-Annotation für SQLAlchemy-Spalten. `Mapped[str]` erzeugt eine `VARCHAR`-Spalte,
`Mapped[int]` eine `INTEGER`-Spalte. Kein separates `Column(...)` nötig – SQLAlchemy
erkennt den Typ aus der Annotation.

**`mapped_column(Identity(start=1000), primary_key=True)`**

- `Identity(start=1000)` → auto-increment Primärschlüssel, startet bei 1000
- `primary_key=True` → markiert die Spalte als Primärschlüssel

**`ForeignKey("kunde.id")`**
Erstellt einen SQL-Fremdschlüssel auf `kunde.id`.

**`unique=True` auf `kunde_id`**
Erzwingt auf Datenbankebene, dass jede Adresse nur einem Kunden gehört (1:1-Beziehung).

**`relationship(back_populates="adresse")`**
Definiert die ORM-Beziehung zurück zum `Kunde`-Objekt.
`back_populates` synchronisiert beide Seiten automatisch – wenn `kunde.adresse` gesetzt wird,
wird auch `adresse.kunde` automatisch befüllt.

**`__repr__`**
Gibt das Objekt als lesbaren String aus. Wichtig: Kein Zugriff auf `self.kunde`,
weil das einen SQL-JOIN auslösen würde.

---

### 1.4 [`entity/bestellung.py`](../../src/kunde/entity/bestellung.py)

```python
"""Entity-Klasse für Bestellung."""

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.base import Base


class Bestellung(Base):
    __tablename__ = "bestellung"

    produktname: Mapped[str]
    menge: Mapped[int]

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )

    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"))

    kunde: Mapped[Kunde] = relationship(
        back_populates="bestellungen",
    )

    def __repr__(self) -> str:
        return (
            f"Bestellung(id={self.id}, produktname={self.produktname}, "
            f"menge={self.menge})"
        )
```

Struktur identisch zu `Adresse`, mit zwei Unterschieden:

**Kein `unique=True` auf `kunde_id`**
Ein Kunde kann mehrere Bestellungen haben → 1:N-Beziehung. `unique=True` würde das verhindern.

**`back_populates="bestellungen"`**
Entspricht dem Feld `bestellungen` in `Kunde` (eine Liste, keine einzelne Instanz).

---

### 1.5 [`entity/kunde.py`](../../src/kunde/entity/kunde.py)

```python
"""Entity-Klasse für Kundendaten."""

from typing import Any, Self

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung


class Kunde(Base):
    __tablename__ = "kunde"

    nachname: Mapped[str]

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(unique=True)

    adresse: Mapped[Adresse] = relationship(
        back_populates="kunde",
        innerjoin=True,
        cascade="save-update, delete",
    )

    bestellungen: Mapped[list[Bestellung]] = relationship(
        back_populates="kunde",
        cascade="save-update, delete",
    )

    version: Mapped[int] = mapped_column(default=0)

    def set(self, kunde: Self) -> None:
        self.nachname = kunde.nachname
        self.email = kunde.email

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id is not None else hash(type(self))

    def __repr__(self) -> str:
        return f"Kunde(id={self.id}, nachname={self.nachname}, email={self.email})"
```

**`id: Mapped[int | None]`**
Die ID ist `None`, solange das Objekt noch nicht in der Datenbank gespeichert ist.
Nach `session.flush()` bekommt es die von der DB vergebene ID.

**`email: Mapped[str] = mapped_column(unique=True)`**
`unique=True` erzeugt auf DB-Ebene einen UNIQUE-Index → keine zwei Kunden mit gleicher Email.

**`adresse: Mapped[Adresse] = relationship(innerjoin=True, cascade="save-update, delete")`**

- `innerjoin=True` → beim Laden des Kunden wird ein INNER JOIN auf `adresse` gemacht. Ein Kunde ohne Adresse ist ungültig.
- `cascade="save-update, delete"` → wenn ein Kunde gespeichert oder gelöscht wird, wird die Adresse automatisch mitgespeichert oder mitgelöscht.

**`bestellungen: Mapped[list[Bestellung]]`**
Eine Liste bedeutet 1:N. Ein Kunde kann null oder mehr Bestellungen haben.
Auch hier `cascade`, damit Bestellungen mitgelöscht werden.

**`version: Mapped[int] = mapped_column(default=0)`**
Wird für **optimistische Nebenläufigkeitskontrolle** genutzt (ETag/If-Match).
Startet bei 0, wird bei jedem Update erhöht. Wird im HTTP-Header als ETag ausgeliefert.

**Warum steht `version` nach `adresse` und `bestellungen`?**
Python-Dataclasses erlauben keine Felder ohne Default nach Felder mit Default.
`adresse` und `bestellungen` haben auf Dataclass-Ebene kein Default → sie müssen vor `version`
(das `default=0` hat) stehen. Sonst: `TypeError: non-default argument follows default argument`.

**`def set(self, kunde: Self) -> None`**
`Self` (aus `typing`) ist der eigene Typ der Klasse. Die Methode kopiert nur die
einfachen Felder (nachname, email) – nicht die Beziehungen. Wird beim Update-Vorgang genutzt.

**`__eq__` und `__hash__`**
Vergleich ausschließlich anhand der ID. Kein Zugriff auf `adresse` oder `bestellungen`,
weil das ungewollte SQL-JOINs auslösen würde.

---

## 2. Repository-Layer

Das Repository ist die einzige Schicht, die SQL-Abfragen baut und ausführt.
Der Service weiß nicht, wie die Daten gespeichert werden – er fragt nur das Repository.

---

### 2.1 [`repository/pageable.py`](../../src/kunde/repository/pageable.py)

```python
"""Steuerungsparameter für paginierte Datenbankabfragen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

__all__ = ["MAX_PAGE_SIZE", "Pageable"]


DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_NUMBER = 0


@dataclass(eq=False, slots=True, kw_only=True)
class Pageable:
    size: int
    number: int

    @staticmethod
    def create(number: str | None = None, size: str | None = None) -> Pageable:
        number_int: Final = (
            DEFAULT_PAGE_NUMBER
            if number is None or not number.isdigit()
            else int(number)
        )
        size_int: Final = (
            DEFAULT_PAGE_SIZE
            if size is None
            or not size.isdigit()
            or int(size) > MAX_PAGE_SIZE
            or int(size) < 0
            else int(size)
        )
        return Pageable(size=size_int, number=number_int)

    @property
    def offset(self) -> int:
        return self.number * self.size
```

**`from __future__ import annotations`**
Macht alle Typ-Annotationen in der Datei zu lazy Strings. Dadurch kann `Pageable` im
Rückgabetyp von `create()` stehen, obwohl die Klasse zu dem Zeitpunkt noch nicht
vollständig definiert ist – kein `"Pageable"` in Anführungszeichen nötig.

**Modul-Konstanten: `DEFAULT_PAGE_SIZE = 5`, `MAX_PAGE_SIZE = 100`, `DEFAULT_PAGE_NUMBER = 0`**
Keine Klasse, keine Kapselung – einfach oben definiert, überall im Modul sichtbar.
`MAX_PAGE_SIZE` wird auch in `__all__` exportiert, damit der Router ihn direkt importieren kann.

**`@dataclass(eq=False, slots=True, kw_only=True)`**

- `eq=False` → kein automatisches `__eq__`. Kein sinnvoller Vergleich zwischen Pageable-Objekten.
- `slots=True` → feste Slots statt `__dict__`, spart Speicher und beschleunigt Zugriff.
- `kw_only=True` → alle Felder müssen als Keyword-Argument übergeben werden:
  `Pageable(size=5, number=0)`, nicht `Pageable(5, 0)`.

**`@staticmethod def create(...)`**
`@staticmethod` weil die Methode kein `self` oder `cls` braucht – sie ist eine Factory-Funktion,
die zufällig in der Klasse wohnt. Beide Parameter sind `str | None`, weil Query-Parameter
aus HTTP-Requests immer als Strings ankommen (oder gar nicht).

**`number_int: Final = ...`**
`Final` bedeutet: diese Variable wird nach der Zuweisung nie mehr geändert.
Das ist eine Absichtserklärung an den Leser und den Typprüfer.

**Validierungslogik für `size_int`**
Vier Fehlerfälle führen zum Default: fehlt, kein Integer, zu groß, negativ.
Nur wenn alle Checks bestehen, wird der Wert übernommen.
`isdigit()` prüft, ob alle Zeichen Ziffern sind (kein try/except nötig).

**`@property def offset(self) -> int`**
`@property` macht `offset` zu einem berechneten Attribut – man schreibt `pageable.offset`,
nicht `pageable.offset()`. Die Formel: Seite 0 → Offset 0, Seite 1 → Offset 5 usw.

---

### 2.2 [`repository/slice.py`](../../src/kunde/repository/slice.py)

```python
"""Paginiertes Ergebnis einer Datenbankabfrage."""

from dataclasses import dataclass

__all__ = ["Slice"]


@dataclass(eq=False, slots=True, kw_only=True)
class Slice[T]:
    content: tuple[T, ...]
    total_elements: int
```

**`class Slice[T]`**
PEP 695-Syntax (Python 3.12) für einen Typparameter – statt dem älteren `class Slice(Generic[T])`.
`T` ist ein Platzhalter für den konkreten Typ des Inhalts, z.B. `Slice[Kunde]` oder `Slice[KundeDTO]`.

**`content: tuple[T, ...]`**
Ein unveränderliches Tupel der Treffer. `tuple[T, ...]` bedeutet: Tupel beliebiger Länge,
jedes Element vom Typ `T`. Tupel statt Liste, weil das Ergebnis nach dem Lesen
nicht mehr verändert werden soll.

**`total_elements: int`**
Die Gesamtzahl aller Treffer in der Datenbank – unabhängig von der aktuellen Seite.
Wird gebraucht, um im Router `total_pages` berechnen zu können.

---

### 2.3 [`repository/kunde_repository.py`](../../src/kunde/repository/kunde_repository.py)

```python
"""Repository für persistente Kundendaten."""

from collections.abc import Mapping
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from kunde.entity import Kunde
from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
```

**`from collections.abc import Mapping`**
Read-only Dict-Supertyp für `suchparameter`. Akzeptiert `dict`, jede Mapping-Implementierung.
Macht die Methode flexibler als wenn sie nur `dict` annehmen würde.

**`from sqlalchemy import func, select`**

- `select` → baut SQL-SELECT-Statements als Python-Objekte
- `func` → SQL-Funktionen wie `COUNT()`

**`from sqlalchemy.orm import Session, joinedload`**

- `Session` → die Datenbankverbindung/Transaktion
- `joinedload` → lädt Beziehungen per JOIN in einer einzigen SQL-Abfrage (Eager Loading)

---

#### [`find_by_id`](../../src/kunde/repository/kunde_repository.py#L20)

```python
def find_by_id(self, kunde_id: int | None, session: Session) -> Kunde | None:
    logger.debug("kunde_id={}", kunde_id)

    if kunde_id is None:
        return None

    statement: Final = (
        select(Kunde)
        .options(
            joinedload(Kunde.adresse),
            joinedload(Kunde.bestellungen),
        )
        .where(Kunde.id == kunde_id)
    )
    kunde: Final = session.scalar(statement)

    logger.debug("{}", kunde)
    return kunde
```

**`select(Kunde)`** → erzeugt `SELECT * FROM kunde` als Python-Objekt (kein String!).

**`.options(joinedload(Kunde.adresse), joinedload(Kunde.bestellungen))`**
Fügt JOINs hinzu, damit Adresse und Bestellungen in einer einzigen SQL-Abfrage geladen werden.
Ohne `joinedload` würden zwei weitere Queries ausgelöst (N+1-Problem).

**`.where(Kunde.id == kunde_id)`** → erzeugt `WHERE id = ?` mit Prepared Statement.

**`session.scalar(statement)`** → gibt genau ein Objekt zurück (oder `None`).

---

#### [`find`](../../src/kunde/repository/kunde_repository.py#L46) – der öffentliche Dispatcher

```python
def find(
    self,
    suchparameter: Mapping[str, str],
    pageable: Pageable,
    session: Session,
) -> Slice[Kunde]:
    if not suchparameter:
        return self._find_all(pageable=pageable, session=session)

    for key, value in suchparameter.items():
        if key == "email":
            kunde = self._find_by_email(email=value, session=session)
            return (
                Slice(content=(kunde,), total_elements=1)
                if kunde is not None
                else Slice(content=(), total_elements=0)
            )
        if key == "nachname":
            return self._find_by_nachname(
                teil=value, pageable=pageable, session=session
            )

    return Slice(content=(), total_elements=0)
```

Das ist die einzige öffentliche Suchmethode. Sie schaut, welche Suchparameter übergeben wurden,
und delegiert an die passende private Methode.

**`if not suchparameter`** → leeres Dict → alle Kunden laden.

**`for key, value in suchparameter.items()`**
Iteration über die Suchparameter. Unbekannte Keys → leerer Slice.
Diese Struktur erlaubt es, später weitere Suchparameter als weiteres `if key == "..."` hinzuzufügen.

**`Slice(content=(kunde,), total_elements=1)`**
`(kunde,)` ist ein Tupel mit einem Element. Das Komma ist wichtig – ohne es wäre es nur eine
Klammerung: `(kunde)` == `kunde`.

---

#### [`_find_all`](../../src/kunde/repository/kunde_repository.py#L84) und [`_find_by_nachname`](../../src/kunde/repository/kunde_repository.py#L141)

```python
def _find_all(self, pageable: Pageable, session: Session) -> Slice[Kunde]:
    offset = pageable.number * pageable.size

    statement: Final = (
        select(Kunde)
        .options(
            joinedload(Kunde.adresse),
            joinedload(Kunde.bestellungen),
        )
        .limit(pageable.size)
        .offset(offset)
        if pageable.size != 0
        else select(Kunde).options(
            joinedload(Kunde.adresse),
            joinedload(Kunde.bestellungen),
        )
    )

    kunden: Final = session.scalars(statement).unique().all()
    anzahl: Final = self._count_all_rows(session)
    kunde_slice: Final = Slice(content=tuple(kunden), total_elements=anzahl)
    return kunde_slice
```

**Ternärer Ausdruck für `statement`**
Wenn `size == 0`: kein LIMIT gesetzt → alle Ergebnisse.
Sonst: SQL `LIMIT` und `OFFSET` für Paginierung.

**`session.scalars(statement).unique().all()`**

- `.scalars()` statt `.scalar()` → gibt mehrere Objekte zurück
- `.unique()` ist **zwingend notwendig** wenn `joinedload` auf eine 1:N-Beziehung (Bestellungen) angewandt wird. Der JOIN erzeugt mehrere Zeilen pro Kunde, und `.unique()` dedupliziert sie. Ohne `.unique()` gibt es einen Laufzeitfehler.
- `.all()` → materialisiert die Ergebnisse als Python-Liste

**`tuple(kunden)`** → konvertiert die Liste in ein unveränderliches Tupel für den `Slice`.

---

#### [`_count_all_rows`](../../src/kunde/repository/kunde_repository.py#L114) und [`_count_rows_nachname`](../../src/kunde/repository/kunde_repository.py#L178)

```python
def _count_all_rows(self, session: Session) -> int:
    statement: Final = select(func.count()).select_from(Kunde)
    count: Final = session.execute(statement).scalar()
    return count if count is not None else 0
```

**`select(func.count()).select_from(Kunde)`**
SQL: `SELECT COUNT(*) FROM kunde`. `.select_from(Kunde)` sagt SQLAlchemy,
von welcher Tabelle gezählt wird.

**`count if count is not None else 0`**
`session.scalar()` kann theoretisch `None` zurückgeben – Fallback auf `0`.

---

#### [`find_nachnamen`](../../src/kunde/repository/kunde_repository.py#L187)

```python
def find_nachnamen(self, teil: str, session: Session) -> list[str]:
    statement: Final = (
        select(Kunde.nachname)
        .where(Kunde.nachname.ilike(f"%{teil}%"))
        .distinct()
    )
    nachnamen: Final = list(session.scalars(statement))
    return nachnamen
```

**`select(Kunde.nachname)`** → selektiert nur die Nachname-Spalte, kein ganzes Objekt.

**`.ilike(f"%{teil}%")`**
`ilike` = case-insensitives LIKE. `%` ist der SQL-Wildcard für beliebige Zeichen.
`%Müll%` findet „Müller", „Mülleimer" usw.

**`.distinct()`** → SQL `DISTINCT` – keine doppelten Nachnamen im Ergebnis.

---

#### [`exists_email`](../../src/kunde/repository/kunde_repository.py#L207) und [`exists_email_other_id`](../../src/kunde/repository/kunde_repository.py#L244)

```python
def exists_email(self, email: str, session: Session) -> bool:
    statement: Final = select(func.count()).where(Kunde.email == email)
    anzahl: Final = session.scalar(statement)
    return anzahl is not None and anzahl > 0

def exists_email_other_id(self, kunde_id: int, email: str, session: Session) -> bool:
    statement: Final = (
        select(func.count())
        .select_from(Kunde)
        .where(Kunde.email == email)
        .where(Kunde.id != kunde_id)
    )
    anzahl: Final = session.scalar(statement)
    return anzahl is not None and anzahl > 0
```

Gibt `bool` zurück. Wird im Service genutzt, um vor dem Anlegen/Aktualisieren
zu prüfen, ob die Email schon vergeben ist.
`exists_email_other_id` schließt den aktuellen Kunden per `.where(Kunde.id != kunde_id)` aus.

---

#### [`create`](../../src/kunde/repository/kunde_repository.py#L223)

```python
def create(self, kunde: Kunde, session: Session) -> Kunde:
    session.add(instance=kunde)
    session.flush(objects=[kunde])
    return kunde
```

**`session.add()`** → registriert das Objekt in der Session (noch kein SQL).

**`session.flush()`** → schreibt es in die DB (innerhalb der Transaktion).
Damit bekommt `kunde.id` den generierten Wert aus der IDENTITY-Spalte,
noch bevor `commit()` aufgerufen wird.

---

#### [`delete_by_id`](../../src/kunde/repository/kunde_repository.py#L284)

```python
def delete_by_id(self, kunde_id: int, session: Session) -> None:
    kunde: Final = self.find_by_id(kunde_id=kunde_id, session=session)
    if kunde is None:
        return
    session.delete(kunde)
    session.flush()
```

Erst laden (damit SQLAlchemy das Objekt kennt), dann löschen.
Da `cascade="save-update, delete"` auf `adresse` und `bestellungen` gesetzt ist,
löscht SQLAlchemy automatisch auch die verknüpfte Adresse und alle Bestellungen.

---

## 3. Service-Layer

Der Service enthält die Geschäftslogik. Er kennt Repository und Entities,
gibt aber nach außen nur DTOs zurück (keine Entities). Er öffnet und schließt Sessions.

---

### 3.1 [`service/exceptions.py`](../../src/kunde/service/exceptions.py)

```python
"""Exceptions in der Geschäftslogik."""

from collections.abc import Mapping

__all__ = [
    "EmailExistsError",
    "NotFoundError",
    "VersionOutdatedError",
]


class EmailExistsError(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Existierende Email: {email}")
        self.email = email


class NotFoundError(Exception):
    def __init__(
        self,
        kunde_id: int | None = None,
        suchparameter: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__("Not Found")
        self.kunde_id = kunde_id
        self.suchparameter = suchparameter


class VersionOutdatedError(Exception):
    def __init__(self, version: int) -> None:
        super().__init__(f"Veraltete Version: {version}")
        self.version = version
```

**Eigene Exception-Klassen statt generischer `Exception`**
Dadurch kann der Router (bzw. FastAPI) gezielt auf bestimmte Fehlertypen reagieren
und die passende HTTP-Antwort (404, 409, 422 ...) zurückgeben.

**`super().__init__(message)`**
Ruft den Konstruktor der Elternklasse `Exception` auf. Der übergebene String ist die
Fehlermeldung, die bei `str(err)` oder im Traceback erscheint.

**`self.email`, `self.kunde_id` usw.**
Speichert den Fehlerwert als Instanzattribut, damit der Exception-Handler im Router
Details auslesen kann (z.B. welche Email schon existiert).

**`NotFoundError` – beide Parameter optional**
Kann mit ID aufgerufen werden: `NotFoundError(kunde_id=42)`,
mit Suchparametern: `NotFoundError(suchparameter={"email": "..."})`,
oder ganz ohne Parameter: `raise NotFoundError`.
Das macht die Klasse für alle Suchen wiederverwendbar.

---

### 3.2 [`service/adresse_dto.py`](../../src/kunde/service/adresse_dto.py)

```python
"""DTO für die Adresse, ohne SQLAlchemy-Decorators."""

from dataclasses import dataclass

from kunde.entity.adresse import Adresse

__all__ = ["AdresseDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class AdresseDTO:
    plz: str
    ort: str

    @classmethod
    def from_adresse(cls, adresse: Adresse) -> "AdresseDTO":
        return cls(plz=adresse.plz, ort=adresse.ort)
```

**Was ist ein DTO?**
Data Transfer Object – eine einfache Datenklasse ohne Datenbanklogik.
Zweck: Die Entity (`Adresse`) enthält SQLAlchemy-Internals (z.B. `kunde_id`, `id`, `kunde`-Rückreferenz).
Das DTO enthält nur die Felder, die der API-Nutzer sehen soll.

**`@classmethod def from_adresse(cls, adresse: Adresse) -> "AdresseDTO"`**
`@classmethod` bekommt die Klasse selbst als erstes Argument (`cls`), nicht eine Instanz.
Das ermöglicht `cls(...)` statt `AdresseDTO(...)` – falls die Klasse einmal vererbt wird,
wird automatisch die Unterklasse verwendet.

`"AdresseDTO"` in Anführungszeichen ist ein **Forward Reference** –
nötig, weil der Rückgabetyp die eigene Klasse ist (die im `if TYPE_CHECKING`-Block stehen könnte).
Mit `from __future__ import annotations` wäre das nicht nötig.

---

### 3.3 [`service/bestellung_dto.py`](../../src/kunde/service/bestellung_dto.py)

```python
"""DTO für die Bestellung, ohne SQLAlchemy-Decorators."""

from dataclasses import dataclass

from kunde.entity.bestellung import Bestellung

__all__ = ["BestellungDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class BestellungDTO:
    produktname: str
    menge: int

    @classmethod
    def from_bestellung(cls, bestellung: Bestellung) -> "BestellungDTO":
        return cls(produktname=bestellung.produktname, menge=bestellung.menge)
```

Identische Struktur wie `AdresseDTO`.
Enthält nur `produktname` und `menge` – keine `id`, kein `kunde_id`, keine Rückreferenz.

---

### 3.4 [`service/kunde_dto.py`](../../src/kunde/service/kunde_dto.py)

```python
"""DTO für die Übertragung von Kundendaten zwischen den Schichten."""

from __future__ import annotations

from dataclasses import dataclass

from kunde.entity.kunde import Kunde
from kunde.service.adresse_dto import AdresseDTO
from kunde.service.bestellung_dto import BestellungDTO

__all__ = ["KundeDTO"]


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
            id=kunde.id,
            nachname=kunde.nachname,
            email=kunde.email,
            version=kunde.version,
            adresse=AdresseDTO.from_adresse(kunde.adresse),
            bestellungen=[
                BestellungDTO.from_bestellung(b) for b in kunde.bestellungen
            ],
        )
```

**`from __future__ import annotations`**
Ermöglicht `KundeDTO` als Rückgabetyp in `from_kunde()` ohne Anführungszeichen.

**`@dataclass` (ohne Parameter)**
Kein `eq=False`, `slots=True` usw. – hier wird der Standard-Dataclass verwendet.
Das ist eine einfachere Form, die für DTOs ausreichend ist.

**`adresse: AdresseDTO`**
Das DTO enthält ein weiteres DTO als Feld – keine Datenbankklasse.
Die Verschachtelung funktioniert, weil `AdresseDTO.from_adresse(...)` die Konvertierung übernimmt.

**`bestellungen: list[BestellungDTO]`**
List Comprehension: `[BestellungDTO.from_bestellung(b) for b in kunde.bestellungen]`
Für jede Bestellung in der Entity-Liste wird ein BestellungDTO erstellt.

---

### 3.5 [`service/kunde_read_service.py`](../../src/kunde/service/kunde_read_service.py)

```python
"""Geschäftslogik zum Lesen von Kundendaten."""

from collections.abc import Mapping, Sequence
from typing import Final

from loguru import logger

from kunde.repository import KundeRepository, Session
from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
from kunde.service.exceptions import NotFoundError
from kunde.service.kunde_dto import KundeDTO

__all__ = ["KundeReadService"]


class KundeReadService:
    def __init__(self, repo: KundeRepository) -> None:
        self.repo: KundeRepository = repo
```

**`__init__` mit Dependency Injection**
Der Service bekommt das Repository übergeben, statt es selbst zu erstellen.
Das ist **Dependency Injection**: Die Abhängigkeit kommt von außen.
Vorteil: Im Test kann man ein Mock-Repository übergeben, ohne den echten Service zu ändern.

---

#### [`KundeReadService.find_by_id`](../../src/kunde/service/kunde_read_service.py#L24)

```python
def find_by_id(self, kunde_id: int) -> KundeDTO:
    logger.debug("kunde_id={}", kunde_id)

    with Session() as session:
        if (
            kunde := self.repo.find_by_id(kunde_id=kunde_id, session=session)
        ) is None:
            message: Final = f"Kein Kunde mit der ID {kunde_id}"
            logger.debug("NotFoundError: {}", message)
            raise NotFoundError(kunde_id=kunde_id)
        kunde_dto: Final = KundeDTO.from_kunde(kunde)
        session.commit()

    logger.debug("{}", kunde_dto)
    return kunde_dto
```

**`with Session() as session:`**
Öffnet eine Datenbanksession (Transaktion). Am Ende des `with`-Blocks wird
die Session automatisch geschlossen (auch bei Exceptions).

**Walrus-Operator `:=`**

```python
if (kunde := self.repo.find_by_id(...)) is None:
```

Weist das Ergebnis `kunde` zu **und** prüft gleichzeitig ob es `None` ist.
Ohne Walrus-Operator wären es zwei separate Zeilen:

```python
kunde = self.repo.find_by_id(...)
if kunde is None:
```

**`raise NotFoundError(kunde_id=kunde_id)`**
Wenn kein Kunde gefunden wurde, wird eine Exception geworfen.
FastAPI fängt diese im Exception-Handler auf und gibt HTTP 404 zurück.

**`KundeDTO.from_kunde(kunde)`**
Konvertiert die Entity in ein DTO – ab hier keine SQLAlchemy-Objekte mehr.

**`session.commit()`**
Schließt die Transaktion erfolgreich ab. Bei Leseoperationen technisch nicht zwingend nötig,
aber Best Practice um die Session sauber zu beenden.

---

#### [`find`](../../src/kunde/service/kunde_read_service.py#L47)

```python
def find(
    self,
    suchparameter: Mapping[str, str],
    pageable: Pageable,
) -> Slice[KundeDTO]:
    with Session() as session:
        kunde_slice: Final = self.repo.find(
            suchparameter=suchparameter, pageable=pageable, session=session
        )
        if len(kunde_slice.content) == 0:
            raise NotFoundError(suchparameter=suchparameter)

        kunden_dto: Final = tuple(
            KundeDTO.from_kunde(kunde) for kunde in kunde_slice.content
        )
        session.commit()

    kunden_dto_slice = Slice(
        content=kunden_dto, total_elements=kunde_slice.total_elements
    )
    return kunden_dto_slice
```

**`tuple(KundeDTO.from_kunde(kunde) for kunde in kunde_slice.content)`**
Das ist ein **Generator-Ausdruck** (keine eckigen Klammern → keine Zwischenliste).
`tuple(...)` materialisiert ihn direkt als Tupel.
Effizienter als zuerst eine Liste zu erstellen und dann in ein Tupel umzuwandeln.

**`Slice(content=kunden_dto, total_elements=...)`**
Baut einen neuen `Slice[KundeDTO]` – gleiche Struktur wie der `Slice[Kunde]` vom Repository,
aber jetzt mit DTOs statt Entities. `total_elements` wird einfach weitergegeben.

---

#### [`find_nachnamen`](../../src/kunde/service/kunde_read_service.py#L81) (Read-Service)

```python
def find_nachnamen(self, teil: str) -> Sequence[str]:
    with Session() as session:
        nachnamen: Final = self.repo.find_nachnamen(teil=teil, session=session)
        session.commit()

    if len(nachnamen) == 0:
        raise NotFoundError
    return nachnamen
```

**`Sequence[str]`**
Read-only Supertyp für `list[str]`. Der Aufrufer kann den Inhalt lesen, aber nicht verändern.
Flexibler als `list[str]` als Rückgabetyp.

---

## 4. Router-Layer

Der Router empfängt HTTP-Requests, ruft den Service auf und gibt HTTP-Antworten zurück.
Er enthält keine Geschäftslogik – nur HTTP-Protokoll-Details.

---

### 4.1 [`router/constants.py`](../../src/kunde/router/constants.py)

```python
"""Konstanten für HTTP-Header im Router."""

from typing import Final

__all__ = [
    "ETAG",
    "IF_MATCH",
    "IF_MATCH_MIN_LEN",
    "IF_NONE_MATCH",
    "IF_NONE_MATCH_MIN_LEN",
]

ETAG: Final = "ETag"
IF_MATCH: Final = "if-match"
IF_MATCH_MIN_LEN: Final = 3
IF_NONE_MATCH: Final = "If-None-Match"
IF_NONE_MATCH_MIN_LEN: Final = 3
```

**Warum Konstanten statt Magic Strings?**
Statt überall `"ETag"` als String hardzucoden, wird der Name einmal definiert.
Bei einem Tippfehler gibt es einen `NameError` beim Import – nicht erst zur Laufzeit im HTTP-Header.

**ETag und If-None-Match**
HTTP-Caching-Mechanismus:

1. Server schickt `ETag: "0"` (die Versionsnummer) mit der Antwort.
2. Client schickt beim nächsten Request `If-None-Match: "0"`.
3. Server vergleicht: gleiche Version → HTTP 304 Not Modified (kein Body, spart Bandbreite).

**`IF_NONE_MATCH_MIN_LEN: Final = 3`**
Ein gültiger ETag-Wert ist z.B. `"0"` (Länge 3: Anführungszeichen + Ziffer + Anführungszeichen).
Die Mindestlänge 3 stellt sicher, dass der Wert syntaktisch korrekt ist.

---

### 4.2 [`router/page.py`](../../src/kunde/router/page.py)

```python
"""Page als Ergebnis einer paginierten REST-Antwort."""

from dataclasses import dataclass
from typing import Any, Final

from kunde.repository.pageable import Pageable

__all__ = ["Page"]


@dataclass
class Page:
    content: tuple[dict[str, Any], ...]
    page_number: int
    page_size: int
    total_elements: int
    total_pages: int

    @classmethod
    def create(
        cls,
        content: tuple[dict[str, Any], ...],
        pageable: Pageable,
        total_elements: int,
    ) -> "Page":
        total_pages: Final = max(
            1, (total_elements + pageable.size - 1) // pageable.size
        )
        return cls(
            content=content,
            page_number=pageable.number,
            page_size=pageable.size,
            total_elements=total_elements,
            total_pages=total_pages,
        )
```

**Warum `Page` und nicht direkt `Slice`?**
`Slice` enthält Entities oder DTOs. `Page` enthält serialisierte `dict`-Objekte
(bereit für JSON) und zusätzliche Paginierungsmetadaten für den API-Nutzer.

**`content: tuple[dict[str, Any], ...]`**
Ein Tupel von Dictionaries. Jedes Dictionary repräsentiert einen Kunden als JSON-kompatibles Objekt.

**`total_pages` Berechnung**

```python
total_pages = max(1, (total_elements + pageable.size - 1) // pageable.size)
```

Das ist die Standard-Formel für "Aufrunden ohne float":

- 15 Elemente, Größe 5 → `(15 + 4) // 5 = 3` → 3 Seiten
- 14 Elemente, Größe 5 → `(14 + 4) // 5 = 3` → 3 Seiten
- 0 Elemente, Größe 5 → `max(1, 0) = 1` → mindestens 1 Seite

`max(1, ...)` stellt sicher, dass es immer mindestens 1 Seite gibt (auch bei 0 Ergebnissen).

---

### 4.3 [`router/kunde_read_router.py`](../../src/kunde/router/kunde_read_router.py)

```python
"""KundeReadRouter."""

from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
from kunde.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from kunde.router.dependencies import get_read_service
from kunde.router.page import Page
from kunde.service import KundeReadService
from kunde.service.kunde_dto import KundeDTO

__all__ = ["kunde_read_router"]

kunde_read_router: Final = APIRouter(tags=["Lesen"])
```

**`APIRouter`**
FastAPI-Konzept: Routen werden nicht direkt an die `app` gehängt, sondern an einen Router.
Der Router wird dann in `fastapi_app.py` mit einem Präfix eingebunden:
`app.include_router(kunde_read_router, prefix="/rest/kunden")`.

**`tags=["Lesen"]`**
Gruppierung in der automatischen API-Dokumentation (Swagger UI unter `/docs`).

---

#### [`get_by_id`](../../src/kunde/router/kunde_read_router.py#L24)

```python
@kunde_read_router.get("/{kunde_id}")
def get_by_id(
    kunde_id: int,
    request: Request,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> Response:
    kunde: Final = service.find_by_id(kunde_id=kunde_id)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        try:
            if int(version) == kunde.version:
                return Response(status_code=status.HTTP_304_NOT_MODIFIED)
        except ValueError:
            logger.debug("invalid version={}", version)

    return JSONResponse(
        content=_kunde_to_dict(kunde),
        headers={ETAG: f'"{kunde.version}"'},
    )
```

**`@kunde_read_router.get("/{kunde_id}")`**
Registriert diese Funktion als HTTP-GET-Handler für `/rest/kunden/{kunde_id}`.
`{kunde_id}` ist ein Pfadparameter – FastAPI konvertiert ihn automatisch zu `int`.

**`Annotated[KundeReadService, Depends(get_read_service)]`**
FastAPI Dependency Injection:

- `Depends(get_read_service)` → FastAPI ruft `get_read_service()` auf und injiziert das Ergebnis.
- `Annotated[..., ...]` → Standard-Python-Typ mit Metadaten.

Der Service wird nicht manuell erstellt – FastAPI übernimmt das.

##### ETag-Prüfung

```python
if_none_match: Final = request.headers.get(IF_NONE_MATCH)
```

Liest den `If-None-Match`-Header aus dem Request.
Syntaxprüfung: muss in `"..."` eingeschlossen sein (mindestens 3 Zeichen).

```python
version = if_none_match[1:-1]   # entfernt die Anführungszeichen
if int(version) == kunde.version:
    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
```

Gleiche Version → 304 Not Modified (kein Body, Client nutzt seinen Cache).

**`JSONResponse(content=..., headers={ETAG: f'"{kunde.version}"'})`**
Gibt JSON zurück und setzt den `ETag`-Header für zukünftige Caching-Prüfungen.

---

#### [`get`](../../src/kunde/router/kunde_read_router.py#L65) – Suche mit Query-Parametern

```python
@kunde_read_router.get("")
def get(request: Request, service: ...) -> JSONResponse:
    query_params: Final = request.query_params

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)

    suchparameter = dict(query_params)
    suchparameter.pop("page", None)
    suchparameter.pop("size", None)

    kunde_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _kunde_slice_to_page(kunde_slice, pageable)
    return JSONResponse(content=result)
```

**`request.query_params`**
FastAPI liest Query-Parameter aus der URL: `/rest/kunden?nachname=Müller&page=0&size=5`

**`suchparameter.pop("page", None)` und `pop("size", None)`**
`page` und `size` sind Paginierungsparameter – sie sollen nicht als Suchfilter weitergegeben werden.
`pop(key, default)` entfernt den Key und gibt seinen Wert zurück (oder `default` wenn nicht vorhanden).

---

#### [`get_nachnamen`](../../src/kunde/router/kunde_read_router.py#L96)

```python
@kunde_read_router.get("/nachnamen/{teil}")
def get_nachnamen(teil: str, service: ...) -> JSONResponse:
    nachnamen: Final = service.find_nachnamen(teil=teil)
    return JSONResponse(content=nachnamen)
```

Einfachster Endpunkt: Teilstring aus URL → Service → JSON-Array der Nachnamen.

---

#### [Hilfsfunktionen](../../src/kunde/router/kunde_read_router.py#L113)

```python
def _kunde_slice_to_page(
    kunde_slice: Slice[KundeDTO],
    pageable: Pageable,
) -> dict[str, Any]:
    kunde_dicts: Final = tuple(_kunde_to_dict(k) for k in kunde_slice.content)
    page: Final = Page.create(
        content=kunde_dicts,
        pageable=pageable,
        total_elements=kunde_slice.total_elements,
    )
    return asdict(obj=page)


def _kunde_to_dict(kunde: KundeDTO) -> dict[str, Any]:
    return {
        "id": kunde.id,
        "nachname": kunde.nachname,
        "email": kunde.email,
        "adresse": {
            "plz": kunde.adresse.plz,
            "ort": kunde.adresse.ort,
        },
        "bestellungen": [
            {"produktname": b.produktname, "menge": b.menge}
            for b in kunde.bestellungen
        ],
    }
```

**`_kunde_to_dict`**
Konvertiert ein `KundeDTO` in ein Dictionary, das JSON-serialisierbar ist.
Beginnt mit `_` → private Funktion, nur innerhalb dieses Moduls gedacht.

**`asdict(obj=page)`**
`dataclasses.asdict()` konvertiert ein Dataclass-Objekt rekursiv in ein Dictionary.
Das `Page`-Dataclass wird damit automatisch in ein JSON-kompatibles Dict umgewandelt.

---

## 5. App

### 5.1 [`fastapi_app.py`](../../src/kunde/fastapi_app.py)

```python
"""MainApp."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from time import time
from typing import Final

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from loguru import logger

from kunde.banner import banner
from kunde.config.dev.db_populate import db_populate
from kunde.config.dev_modus import dev_db_populate, dev_keycloak_populate
from kunde.problem_details import create_problem_details
from kunde.repository import engine
from kunde.router.kunde_read_router import kunde_read_router
from kunde.router.kunde_write_router import kunde_write_router
from kunde.service.exceptions import EmailExistsError, NotFoundError
```

**Imports auf einen Blick:**

- `AsyncGenerator` → Typ für asynchrone Generatoren (Lifespan)
- `asynccontextmanager` → Decorator für asynchrone Context Manager
- `GZipMiddleware` → komprimiert Antworten automatisch
- `FileResponse` → sendet Dateien als HTTP-Response
- `engine` → SQLAlchemy-Datenbankengine (für `dispose()` beim Shutdown)

---

#### [Lifespan](../../src/kunde/fastapi_app.py#L34)

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    if dev_db_populate:
        db_populate()
    banner(app.routes)
    yield
    logger.info("Der Server wird heruntergefahren.")
    engine.dispose()
```

**`@asynccontextmanager`**
Macht eine async-Generatorfunktion zu einem Context Manager.
FastAPI ruft `lifespan` beim Start und Shutdown auf.

**Alles vor `yield`** → wird beim **Serverstart** ausgeführt:

- Datenbank befüllen (wenn `dev_db_populate=True`)
- Banner in der Konsole ausgeben

**Alles nach `yield`** → wird beim **Shutdown** ausgeführt:

- Engine trennen (Datenbankverbindungen freigeben)

```python
app: Final = FastAPI(lifespan=lifespan)
```

Erstellt die FastAPI-Instanz und übergibt die Lifespan-Funktion.

---

#### [Middleware](../../src/kunde/fastapi_app.py#L51)

```python
app.add_middleware(GZipMiddleware, minimum_size=500)
```

Komprimiert HTTP-Antworten mit GZip, wenn sie mindestens 500 Bytes groß sind.
Spart Bandbreite bei großen JSON-Antworten.

```python
@app.middleware("http")
async def log_request(request: Request, call_next: ...) -> Response:
    logger.debug(f"{request.method} '{request.url}'")
    return await call_next(request)
```

**Middleware-Konzept:**
Jeder HTTP-Request durchläuft alle Middlewares, bevor er den eigentlichen Handler erreicht.
`call_next(request)` gibt den Request an die nächste Middleware/den Handler weiter.

`log_request` loggt Methode und URL. `log_response_time` misst die Bearbeitungszeit in Millisekunden:

```python
start = time()
response = await call_next(request)
duration_ms = (time() - start) * 1000
```

---

#### [Router einbinden](../../src/kunde/fastapi_app.py#L91)

```python
app.include_router(kunde_read_router, prefix="/rest/kunden")
app.include_router(kunde_write_router, prefix="/rest")

if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")
```

Alle Routen aus `kunde_read_router` bekommen den Präfix `/rest/kunden`.
`get("/{kunde_id}")` wird damit zu `/rest/kunden/{kunde_id}`.

Der Dev-Router wird nur registriert wenn `dev_db_populate=True` –
in Produktion gibt es diese Endpunkte nicht.

---

#### [Exception-Handler](../../src/kunde/fastapi_app.py#L125)

```python
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, _err: NotFoundError) -> Response:
    return create_problem_details(status_code=status.HTTP_404_NOT_MODIFIED)


@app.exception_handler(EmailExistsError)
def email_exists_error_handler(_request: Request, err: EmailExistsError) -> Response:
    return create_problem_details(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(err),
    )
```

**`@app.exception_handler(ExceptionType)`**
Wenn irgendwo im Code (Service, Repository, Router) eine `NotFoundError` geworfen wird,
fängt FastAPI sie automatisch ab und ruft diesen Handler auf.
Der Handler gibt eine standardisierte HTTP-Fehlerantwort zurück.

**`_request` und `_err`** (mit Unterstrich)
Der Unterstrich signalisiert: dieser Parameter wird nicht verwendet.
Python-Konvention für unbenutzte Variablen. Bei `EmailExistsError` hingegen wird
`err` gebraucht, um die Fehlermeldung mit `str(err)` auszulesen.

**`create_problem_details`**
Erzeugt eine RFC 7807-konforme Fehlerantwort (Problem Details for HTTP APIs).
Standard-Format für strukturierte Fehlermeldungen in REST-APIs.

---

## Zusammenfassung: Datenfluss bei `GET /rest/kunden/1`

```plaintext
1. HTTP GET /rest/kunden/1
        │
        ▼
2. get_by_id(kunde_id=1)              ← Router
        │ ruft auf
        ▼
3. KundeReadService.find_by_id(1)     ← Service öffnet Session
        │ ruft auf
        ▼
4. KundeRepository.find_by_id(1)      ← Repository baut SQL
        │ SQL: SELECT * FROM kunde
        │      JOIN adresse ...
        │      WHERE id = 1
        ▼
5. Datenbank gibt Zeile zurück
        │
        ▼
6. Kunde-Entity (SQLAlchemy-Objekt)   ← Repository gibt zurück
        │
        ▼
7. KundeDTO.from_kunde(kunde)         ← Service konvertiert
        │
        ▼
8. _kunde_to_dict(kunde_dto)          ← Router serialisiert
        │
        ▼
9. JSONResponse mit ETag-Header       ← HTTP Response
```

# Code-Walkthrough: Kundenverwaltung

Dieses Dokument erklärt jede Datei des Projekts – Block für Block, Zeile für Zeile.
Reihenfolge: Entity → Repository → Service → Router → App

Disclaimer: Diese Erklärung ist von Claude Code generiert worden.

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

#### Imports: Was wird benötigt?

```python
from typing import TYPE_CHECKING, Any
from sqlalchemy.orm import DeclarativeBase
```

Die erste Zeile importiert zwei Dinge aus Pythons `typing`-Modul. `TYPE_CHECKING` ist eine
spezielle Konstante, die zur Laufzeit immer `False` ist – sie wird nur `True`, wenn ein
statischer Typprüfer wie Pylance oder mypy den Code analysiert, ohne ihn auszuführen.
`Any` ist ein Typ, der für "beliebiger Typ" steht und hier nur für den Stub-Konstruktor
gebraucht wird.

Die zweite Zeile importiert `DeclarativeBase` aus SQLAlchemy. Das ist die Basisklasse des
ORM-Systems: Jede Klasse, die davon erbt, wird automatisch im ORM-Registry registriert
und kann auf eine Datenbanktabelle gemappt werden.

#### Der TYPE_CHECKING-Trick

```python
if TYPE_CHECKING:
    class MappedAsDataclass:
        def __init__(self, *arg: Any, **kw: Any) -> None: ...
else:
    from sqlalchemy.orm import MappedAsDataclass
```

Dieser Block löst ein konkretes Problem mit IDEs und statischen Typprüfern.
`MappedAsDataclass` aus SQLAlchemy trägt sogenannte PEP 681-Annotationen, die dem
Typprüfer sagen: "Behandle Unterklassen wie Python-Dataclasses." Das klingt hilfreich,
ist aber manchmal zu streng – der Typprüfer beschwert sich über die Reihenfolge von
Feldern mit und ohne Default-Werte, obwohl der Code zur Laufzeit einwandfrei funktioniert.

Die Lösung: Zur Typprüfzeit (wenn `TYPE_CHECKING` True ist) sieht der Typprüfer nur einen
harmlosen leeren Stub ohne PEP 681-Annotationen. Zur Laufzeit greift der `else`-Zweig und
importiert das echte `MappedAsDataclass` aus SQLAlchemy. Der laufende Code benutzt also
immer die echte Klasse, während der Typprüfer eine vereinfachte Version sieht.

#### Definition der Basisklasse

```python
class Base(MappedAsDataclass, DeclarativeBase):
    """Basisklasse für Entity-Klassen als dataclass."""
```

Diese Zeile kombiniert beide Mixins in einer einzigen Klasse namens `Base`. Durch
Mehrfachvererbung bekommt `Base` die Funktionen beider Elternklassen gleichzeitig.

`MappedAsDataclass` sorgt dafür, dass alle Unterklassen wie Python-Dataclasses behandelt
werden: Felder werden automatisch zum Konstruktor, Objekte können verglichen werden,
und man bekommt eine lesbare Textdarstellung umsonst dazu.

`DeclarativeBase` registriert alle Unterklassen im SQLAlchemy-ORM-System und ermöglicht
es, Klassen direkt zu Datenbanktabellen zu mappen.

Alle Entity-Klassen des Projekts (`Adresse`, `Bestellung`, `Kunde`) erben von `Base` und
bekommen dadurch beides auf einmal: ORM-Mapping und Dataclass-Verhalten.

---

### 1.2 [`entity/__init__.py`](../../src/kunde/entity/__init__.py)

#### Imports und öffentliche API des Pakets

```python
"""Modul für persistente kundendaten."""

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung
from kunde.entity.kunde import Kunde
```

Die vier `from`-Imports holen alle Entity-Klassen in den Namensraum des `entity`-Pakets.
Ohne diese Zeilen wären die Klassen nur über ihren vollständigen Pfad erreichbar, zum
Beispiel `from kunde.entity.kunde import Kunde`. Das funktioniert, ist aber umständlich.

```python
__all__ = [
    "Adresse",
    "Base",
    "Bestellung",
    "Kunde",
]
```

`__all__` ist eine spezielle Python-Variable, die die öffentliche API des Moduls festlegt.
Sie hat zwei Effekte: Erstens kontrolliert sie, was exportiert wird, wenn jemand
`from kunde.entity import *` schreibt – nur die aufgelisteten Namen werden weitergegeben.
Zweitens dient sie als maschinenlesbare Dokumentation: Jeder der diesen Code liest,
sieht auf den ersten Blick, welche Klassen nach außen gedacht sind.

Das praktische Ergebnis: Statt `from kunde.entity.kunde import Kunde` reicht jetzt
`from kunde.entity import Kunde`. Der Importpfad wird kürzer, übersichtlicher und
ändert sich nicht, wenn die Datei intern umstrukturiert wird.

---

### 1.3 [`entity/adresse.py`](../../src/kunde/entity/adresse.py)

#### Imports der Adresse-Klasse

```python
from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.base import Base
```

`ForeignKey` und `Identity` kommen aus dem Kern von SQLAlchemy. `ForeignKey` erstellt
Fremdschlüssel-Beziehungen zwischen Tabellen auf Datenbankebene. `Identity` aktiviert
automatisch inkrementierende Primärschlüssel – die Datenbank vergibt IDs selbst, ohne
dass der Code sie setzen muss.

`Mapped`, `mapped_column` und `relationship` kommen aus dem ORM-Teil von SQLAlchemy.
`Mapped[T]` ist eine Typ-Annotation, die einer Klassen-Variable sagt: "Das ist eine
Datenbankspalte vom Typ T." `mapped_column` konfiguriert diese Spalte mit Optionen wie
`unique=True` oder `primary_key=True`. `relationship` definiert Verknüpfungen zwischen
zwei Entity-Klassen auf Python-Ebene.

#### Klassen-Definition und Tabellenname

```python
class Adresse(Base):
    """Entity-Klasse für die Adresse."""

    __tablename__ = "adresse"
```

`class Adresse(Base)` erbt von der Basisklasse, die wir gerade in `base.py` erklärt
haben. Durch diese Vererbung weiß SQLAlchemy, dass `Adresse` eine Datenbankklasse ist,
und der Python-Interpreter behandelt sie als Dataclass.

`__tablename__ = "adresse"` ist der Name der Datenbanktabelle. SQLAlchemy sucht in der
Datenbank nach einer Tabelle mit genau diesem Namen. Alle `SELECT`-, `INSERT`- und
`UPDATE`-Befehle, die SQLAlchemy für diese Klasse erzeugt, beziehen sich auf diese Tabelle.

#### Die einfachen Text-Felder

```python
    strasse: Mapped[str]
    hausnummer: Mapped[str]
    plz: Mapped[str]
    ort: Mapped[str]
```

Diese vier Zeilen definieren vier Datenbankspalten als Typ-Annotationen. `Mapped[str]`
sagt SQLAlchemy: "Das ist eine Textspalte." SQLAlchemy übersetzt `str` automatisch in den
passenden Datenbanktyp – meistens `VARCHAR`.

Es fällt auf, dass kein `mapped_column(...)` verwendet wird. Das ist kein Fehler: Wenn
keine besonderen Optionen nötig sind (kein `unique=True`, kein `primary_key=True`), reicht
die Typ-Annotation allein aus. SQLAlchemy erkennt `Mapped[str]` und erstellt die Spalte
mit vernünftigen Standard-Einstellungen.

Außerdem: Die Felder stehen ohne Default-Wert ganz oben. Das ist wichtig für die
Dataclass-Mechanik – Felder ohne Default müssen vor Felder mit Default kommen.

#### Der Primärschlüssel

```python
    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
```

Hier brauchen wir `mapped_column(...)`, weil zwei besondere Optionen gesetzt werden.

`Identity(start=1000)` aktiviert eine automatisch inkrementierende Sequenz in der
Datenbank. Die erste Adresse bekommt die ID 1000, die zweite 1001, usw. Der Wert 1000
als Start ist eine bewusste Entscheidung: IDs unter 1000 bleiben für Testdaten reserviert,
die man fest in der Datenbank eintragen kann, ohne mit automatisch vergebenen IDs zu kollidieren.

`primary_key=True` markiert diese Spalte als Primärschlüssel der Tabelle. Das bedeutet:
jede Adresse hat genau eine eindeutige ID, und die Datenbank kann damit Zeilen schnell
suchen und Beziehungen verknüpfen.

#### Der Fremdschlüssel zur Kunden-Tabelle

```python
    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"), unique=True)
```

`ForeignKey("kunde.id")` erstellt einen echten SQL-Fremdschlüssel. Das bedeutet: Die
Datenbank selbst erzwingt, dass jeder Wert in der Spalte `kunde_id` auch als `id` in
der `kunde`-Tabelle existiert. Wenn man versucht eine Adresse zu speichern, die auf
einen nicht-existierenden Kunden verweist, gibt die Datenbank einen Fehler.

`unique=True` ist der entscheidende Unterschied zur `Bestellung`-Entity: Kein Kunde
kann zwei Adressen haben, weil dieselbe `kunde_id` in der `adresse`-Tabelle nicht
zweimal vorkommen darf. Das erzwingt eine 1:1-Beziehung auf Datenbankebene.

#### Die ORM-Beziehung zurück zum Kunden

```python
    kunde: Mapped[Kunde] = relationship(
        back_populates="adresse",
    )
```

Während `kunde_id` die Verbindung auf SQL-Ebene herstellt (eine Zahl in der Datenbank),
gibt `relationship(...)` dem Python-Code Zugriff auf das tatsächliche `Kunde`-Objekt.
Man kann dann `adresse.kunde.nachname` schreiben, anstatt selbst eine Datenbankabfrage
zu schreiben, um den Kunden anhand der `kunde_id` zu suchen.

`back_populates="adresse"` sagt SQLAlchemy, dass diese Beziehung mit dem Feld `adresse`
in der `Kunde`-Klasse verbunden ist. Wenn man `kunde.adresse = new_adresse` setzt, setzt
SQLAlchemy automatisch auch `new_adresse.kunde = kunde` – und umgekehrt. Beide Seiten
bleiben immer synchron, ohne dass man es manuell tun muss.

#### Die Textdarstellung

```python
    def __repr__(self) -> str:
        return (
            f"Adresse(id={self.id}, strasse={self.strasse}, "
            f"hausnummer={self.hausnummer}, plz={self.plz}, ort={self.ort})"
        )
```

`__repr__` definiert, wie das Objekt als Text dargestellt wird – etwa im Debugger oder
beim Loggen mit `logger.debug("{}", adresse)`. Die Methode gibt einen lesbaren String
mit allen relevanten Feldern zurück.

Auffällig ist, was fehlt: `self.kunde` wird nicht ausgegeben. Das ist bewusst so. Würde
man `self.kunde` aufrufen, würde SQLAlchemy bei einem "lazy-loaded" Objekt automatisch
eine SQL-Abfrage auslösen, um den Kunden aus der Datenbank zu laden. Das wäre unerwartet
langsam und könnte sogar einen Fehler verursachen, wenn keine aktive Session mehr offen ist.
Deswegen zeigt `__repr__` nur die Felder, die bereits im Speicher liegen.

---

### 1.4 [`entity/bestellung.py`](../../src/kunde/entity/bestellung.py)

#### Struktur und Unterschiede zur Adresse

```python
class Bestellung(Base):
    __tablename__ = "bestellung"

    produktname: Mapped[str]
    menge: Mapped[int]

    id: Mapped[int] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    kunde_id: Mapped[int] = mapped_column(ForeignKey("kunde.id"))
```

Die Struktur ist fast identisch mit `Adresse`. Beide haben einen auto-inkrementierenden
Primärschlüssel und einen Fremdschlüssel auf die `kunde`-Tabelle. Der entscheidende
Unterschied steckt in einer fehlenden Option: `kunde_id` hat hier kein `unique=True`.

Das ist der Mechanismus, der eine 1:N-Beziehung implementiert. Ohne `unique=True` kann
dieselbe `kunde_id` in der Bestellungs-Tabelle beliebig oft vorkommen – jede Zeile ist
eine eigene Bestellung desselben Kunden. Bei `Adresse` war `unique=True` gesetzt, weil
jede Adresse eindeutig einem Kunden gehören soll.

#### ORM-Beziehung und Textdarstellung

```python
    kunde: Mapped[Kunde] = relationship(
        back_populates="bestellungen",
    )

    def __repr__(self) -> str:
        return (
            f"Bestellung(id={self.id}, produktname={self.produktname}, "
            f"menge={self.menge})"
        )
```

`back_populates="bestellungen"` – der Feldname ist Plural, weil das entsprechende Feld
in der `Kunde`-Klasse `bestellungen` heißt und eine Liste enthält. `adresse` war Singular,
weil Kunde genau eine Adresse hat. Dieser Namenunterschied spiegelt die Art der Beziehung
direkt im Code wider.

Auch hier fehlt `self.kunde` in `__repr__` aus demselben Grund wie bei `Adresse`: um
ungewollte SQL-Abfragen zu vermeiden.

---

### 1.5 [`entity/kunde.py`](../../src/kunde/entity/kunde.py)

#### Imports der Kunden-Klasse

```python
from typing import Any, Self

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kunde.entity.adresse import Adresse
from kunde.entity.base import Base
from kunde.entity.bestellung import Bestellung
```

`Self` ist ein spezieller Typ aus Python's `typing`-Modul. Er steht für "den eigenen Typ
dieser Klasse" und wird in der `set()`-Methode verwendet. Wenn man stattdessen `Kunde`
schreiben würde, hätte man einen zirkulären Import-Fehler, weil `Kunde` sich selbst noch
nicht kennen kann, während die Klasse definiert wird. `Self` löst das elegant.

`Adresse` und `Bestellung` werden importiert, weil `Kunde` Beziehungen zu beiden Klassen
hat und SQLAlchemy die Klassen kennen muss, um die Joins bauen zu können.

#### Klassen-Definition und einfache Felder

```python
class Kunde(Base):
    __tablename__ = "kunde"

    nachname: Mapped[str]
```

Die Struktur folgt dem gleichen Muster wie `Adresse` und `Bestellung`. `__tablename__`
legt den Tabellennamen fest. `nachname: Mapped[str]` ist das erste einfache Feld ohne
besondere Konfiguration – eine normale Textspalte in der Datenbank.

#### Der besondere Primärschlüssel

```python
    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
```

Hier gibt es einen wichtigen Unterschied zu `Adresse` und `Bestellung`: Der Typ ist
`int | None`, nicht einfach `int`. Das `None` hat einen konkreten Grund.

Wenn man ein neues `Kunde`-Objekt im Python-Code erstellt, existiert es noch nicht in der
Datenbank. Die ID wird erst von der Datenbank vergeben, wenn das Objekt gespeichert wird
(genauer: wenn `session.flush()` aufgerufen wird). Bevor das passiert, hat das Objekt
keine ID – also ist sie `None`. Der Typ `int | None` drückt genau diesen Zustand aus:
"Entweder hat dieses Objekt eine ID, oder es wurde noch nicht gespeichert."

#### Das eindeutige Email-Feld

```python
    email: Mapped[str] = mapped_column(unique=True)
```

`mapped_column(unique=True)` erzeugt auf Datenbankebene einen UNIQUE-Index auf der
`email`-Spalte. Das bedeutet: Die Datenbank selbst verhindert, dass zwei Kunden dieselbe
E-Mail-Adresse haben. Auch wenn der Python-Code vergisst, das zu prüfen, würde ein
Datenbankfehler ausgelöst.

Warum trotzdem im Service prüfen (mit `exists_email()`)? Weil ein Datenbankfehler eine
generische Fehlermeldung produziert, während die Service-Prüfung eine fachliche Exception
(`EmailExistsError`) wirft, die im Router zu einer verständlichen HTTP-Antwort wird.

#### Die Adresse-Beziehung

```python
    adresse: Mapped[Adresse] = relationship(
        back_populates="kunde",
        innerjoin=True,
        cascade="save-update, delete",
    )
```

Diese Beziehung hat drei Optionen, und jede hat eine eigene Bedeutung.

`back_populates="kunde"` verbindet diese Seite der Beziehung mit dem `kunde`-Feld in
der `Adresse`-Klasse – dieselbe Mechanik wie zuvor erklärt.

`innerjoin=True` ändert, wie SQLAlchemy die Adresse beim Laden eines Kunden holt.
Normalerweise verwendet SQLAlchemy einen LEFT OUTER JOIN – der Kunde wird geladen, auch
wenn keine Adresse vorhanden ist. Mit `innerjoin=True` wird stattdessen ein INNER JOIN
verwendet: Wenn kein Adresse-Eintrag existiert, liefert die Abfrage gar kein Ergebnis.
Das erzwingt effektiv, dass jeder Kunde eine Adresse haben muss.

`cascade="save-update, delete"` steuert, was passiert, wenn ein Kunde gespeichert oder
gelöscht wird. "save-update" bedeutet: Wenn der Kunde gespeichert wird, wird seine Adresse
automatisch mitgespeichert. "delete" bedeutet: Wenn der Kunde gelöscht wird, wird seine
Adresse automatisch mitgelöscht. Ohne diese Option müsste man die Adresse immer manuell
vor dem Kunden löschen, sonst würde die Datenbank einen Fremdschlüssel-Fehler werfen.

#### Die Bestellungs-Beziehung

```python
    bestellungen: Mapped[list[Bestellung]] = relationship(
        back_populates="kunde",
        cascade="save-update, delete",
    )
```

`Mapped[list[Bestellung]]` – die eckigen Klammern mit `list` sind der Unterschied zur
Adresse. Ein `Kunde` hat eine `Adresse` (Singular, 1:1), aber er hat `bestellungen`
(Plural, eine Liste, 1:N). SQLAlchemy erkennt `list[Bestellung]` und weiß: Das ist eine
Eins-zu-Viele-Beziehung. Beim Laden des Kunden werden alle seine Bestellungen als
Python-Liste in diesem Feld gespeichert.

`innerjoin=True` fehlt hier bewusst. Ein Kunde ohne Bestellungen ist völlig valid. Mit
`innerjoin=True` würde ein Kunde ohne Bestellungen beim Laden verschwinden.

#### Das Versions-Feld

```python
    version: Mapped[int] = mapped_column(default=0)
```

Dieses Feld ist für das Concurrency-Konzept zuständig. "Optimistische Nebenläufigkeitskontrolle"
bedeutet: Wenn zwei Benutzer gleichzeitig denselben Kunden bearbeiten, soll verhindert
werden, dass die Änderungen eines Benutzers die des anderen unbemerkt überschreiben.

Das Prinzip: Jeder Kunde startet mit Version 0. Wenn ein Client einen Kunden lädt,
bekommt er auch die aktuelle Version. Wenn er den Kunden speichern will, schickt er die
Version mit (`If-Match: "0"`). Der Server prüft, ob die Version noch aktuell ist. Wenn
nicht – weil jemand anderes zwischenzeitlich gespeichert hat – gibt es einen 409 Conflict.

`default=0` gibt diesem Feld einen Startwert. Das macht `version` zu einem Feld mit
Default-Wert, was erklärt, warum es nach `adresse` und `bestellungen` stehen muss:
Python-Dataclasses verlangen, dass Felder ohne Default vor Felder mit Default kommen.

#### Die set()-Methode

```python
    def set(self, kunde: Self) -> None:
        self.nachname = kunde.nachname
        self.email = kunde.email
```

Diese Methode wird beim Update-Vorgang genutzt. Wenn ein Kunde aktualisiert werden soll,
lädt der Service den bestehenden Kunden aus der Datenbank (`kunde_db`) und erstellt aus
dem Request-Body ein temporäres `Kunde`-Objekt (`kunde`). Dann ruft er `kunde_db.set(kunde)`
auf, um die primitiven Felder des Datenbank-Kunden zu überschreiben.

Warum nicht einfach `kunde_db.nachname = request.nachname` direkt schreiben? Die
`set()`-Methode kapselt diese Logik an einer zentralen Stelle. Wenn später ein neues
Feld hinzukommt, das beim Update veränderbar sein soll, muss man nur diese Methode
anpassen, nicht alle Stellen im Code, die Updates durchführen.

`Self` statt `Kunde` als Typ: Das funktioniert auch, wenn `Kunde` eine Unterklasse
bekommt – die Methode akzeptiert dann automatisch Instanzen der Unterklasse.

#### Vergleich und Hash

```python
    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id is not None else hash(type(self))
```

`__eq__` definiert, wann zwei `Kunde`-Objekte als gleich gelten. Die drei Zeilen prüfen
der Reihe nach:

Die erste Prüfung `if self is other` ist eine Optimierung: Wenn beide Variablen auf
dasselbe Python-Objekt im Speicher zeigen, sind sie trivialerweise gleich.

Die zweite Prüfung `if not isinstance(other, type(self))` stellt sicher, dass man
keinen `Kunde` mit einem komplett anderen Objekt vergleicht – das würde immer `False`
ergeben müssen.

Die dritte Zeile ist der eigentliche Vergleich: Zwei Kunden sind gleich, wenn ihre IDs
gleich sind. Das ist fachlich korrekt, weil die ID der Primärschlüssel ist. `self.id is not None`
verhindert, dass zwei noch-nicht-gespeicherte Kunden (beide `id=None`) als gleich gelten.

`__hash__` muss immer zusammen mit `__eq__` definiert werden, wenn man `__eq__` überschreibt.
Sonst können Objekte nicht in Sets oder als Dictionary-Keys verwendet werden. Der Hash
basiert ebenfalls auf der ID – Objekte, die laut `__eq__` gleich sind, müssen denselben
Hash-Wert haben.

---

## 2. Repository-Layer

Das Repository ist die einzige Schicht, die SQL-Abfragen baut und ausführt.
Der Service weiß nicht, wie die Daten gespeichert werden – er fragt nur das Repository.

---

### 2.1 [`repository/pageable.py`](../../src/kunde/repository/pageable.py)

#### Imports und Modul-Konstanten

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Final

DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_NUMBER = 0
```

`from __future__ import annotations` ist ein spezielles Zukunfts-Import, das alle
Typ-Annotationen in der Datei zu "lazy strings" macht. Das bedeutet: Python wertet sie
nicht sofort aus, sondern behandelt sie als Text. Das ermöglicht, dass `Pageable` im
Rückgabetyp von `create()` stehen kann, obwohl die Klasse zu diesem Zeitpunkt im Code
noch nicht vollständig definiert ist. Ohne diesen Import müsste man `"Pageable"` in
Anführungszeichen schreiben.

Die drei Konstanten sind einfache Modul-Variablen, keine Klassen-Attribute. `DEFAULT_PAGE_SIZE = 5`
bedeutet: Wenn der Client keine Seitengröße angibt, werden 5 Einträge zurückgegeben.
`MAX_PAGE_SIZE = 100` ist eine Sicherheitsbeschränkung – kein Client kann mehr als 100
Einträge auf einmal abrufen, um die Datenbank nicht zu überlasten.

#### Die Klassen-Definition

```python
@dataclass(eq=False, slots=True, kw_only=True)
class Pageable:
    size: int
    number: int
```

Der `@dataclass`-Decorator mit seinen Parametern verdient eine genaue Erklärung.

`eq=False` deaktiviert die automatische Generierung von `__eq__`. Das bedeutet: Zwei
`Pageable`-Objekte kann man nicht mit `==` vergleichen. Das ist sinnvoll, weil kein
Szenario existiert, in dem man zwei Pageable-Objekte auf Gleichheit prüfen müsste.

`slots=True` sorgt dafür, dass die Klasse intern `__slots__` statt `__dict__` verwendet.
Jede normale Python-Klasse hat ein `__dict__`-Attribut, das alle Instanz-Variablen als
dynamisches Dictionary speichert. Mit `slots=True` werden stattdessen feste "Slots"
angelegt – das spart Arbeitsspeicher und macht den Zugriff auf die Attribute etwas schneller.

`kw_only=True` erzwingt, dass alle Felder als Keyword-Argumente übergeben werden müssen:
`Pageable(size=5, number=0)` funktioniert, aber `Pageable(5, 0)` nicht. Das macht den
Code lesbarer – man sieht beim Aufruf sofort, welcher Wert für was steht.

#### Die Validierungslogik: Seitennummer

```python
    @staticmethod
    def create(number: str | None = None, size: str | None = None) -> Pageable:
        number_int: Final = (
            DEFAULT_PAGE_NUMBER
            if number is None or not number.isdigit()
            else int(number)
        )
```

`@staticmethod` sagt: Diese Methode gehört zur Klasse, braucht aber weder `self` (eine
Instanz) noch `cls` (die Klasse selbst). Sie ist eine Factory-Funktion, die zufällig
innerhalb der Klasse definiert ist, um den Code zu gruppieren.

Die Parameter sind `str | None`, weil Query-Parameter aus HTTP-Requests immer als Text
ankommen. Die URL `?page=2` liefert den String `"2"`, nicht die Zahl `2`. Und wenn der
Parameter gar nicht mitgeschickt wird, ist er `None`.

`number_int: Final = ...` – `Final` ist eine Typ-Annotation, die sagt: "Diese Variable
wird nach der Zuweisung nie mehr geändert." Das ist eine Aussage an den Typprüfer und
an den Leser: Ich mache das bewusst unveränderlich.

Der ternäre Ausdruck liest sich von links nach rechts als: "Nimm `DEFAULT_PAGE_NUMBER`,
wenn `number` fehlt oder keine gültige Ganzzahl ist, sonst konvertiere den String zu `int`."
`number.isdigit()` prüft, ob alle Zeichen des Strings Ziffern sind – das ist schneller
und sicherer als `try: int(number) except ValueError`.

#### Die Validierungslogik: Seitengröße

```python
        size_int: Final = (
            DEFAULT_PAGE_SIZE
            if size is None
            or not size.isdigit()
            or int(size) > MAX_PAGE_SIZE
            or int(size) < 0
            else int(size)
        )
        return Pageable(size=size_int, number=number_int)
```

Die Validierung für `size` hat vier Fehlerfälle, die alle zum Default `DEFAULT_PAGE_SIZE`
führen: Der Parameter fehlt, er enthält keine Ziffern, er ist größer als das Maximum, oder
er ist negativ. Nur wenn alle vier Bedingungen nicht zutreffen, wird der Wert übernommen.

`return Pageable(size=size_int, number=number_int)` erstellt das validierte Pageable-Objekt.
Die Keywords (`size=`, `number=`) sind dank `kw_only=True` zwingend erforderlich.

#### Die offset-Eigenschaft

```python
    @property
    def offset(self) -> int:
        return self.number * self.size
```

`@property` macht `offset` zu einem berechneten Attribut. Man ruft es wie ein Feld ab
(`pageable.offset`), ohne Klammern, aber im Hintergrund führt Python die Berechnung aus.

Die Formel ist simpel: Wenn man sich auf Seite 2 befindet (`number=2`) und jede Seite
5 Einträge hat (`size=5`), dann soll die Abfrage bei Eintrag Nummer 10 starten
(`offset = 2 * 5 = 10`). Das entspricht genau dem SQL-Schlüsselwort `OFFSET`.

---

### 2.2 [`repository/slice.py`](../../src/kunde/repository/slice.py)

#### Das generische Ergebnis-Container

```python
@dataclass(eq=False, slots=True, kw_only=True)
class Slice[T]:
    content: tuple[T, ...]
    total_elements: int
```

`class Slice[T]` verwendet die PEP 695-Syntax aus Python 3.12 für generische Klassen.
`[T]` ist ein Typparameter – ein Platzhalter für den konkreten Inhalt. Man kann
`Slice[Kunde]` oder `Slice[KundeDTO]` schreiben und der Typprüfer weiß, welchen Typ
`content` enthält. Die ältere Schreibweise wäre `class Slice(Generic[T])` mit einem
zusätzlichen Import.

`content: tuple[T, ...]` – `tuple[T, ...]` bedeutet: Ein Tupel beliebiger Länge, bei
dem jedes Element vom Typ `T` ist. Tupel statt Liste, weil das Ergebnis nach dem Lesen
nicht mehr verändert werden soll. Eine Liste wäre veränderbar und könnte nach der
Rückgabe aus dem Repository noch befüllt oder geleert werden – das soll nicht passieren.

`total_elements: int` speichert die Gesamtzahl aller Treffer in der Datenbank, unabhängig
von der aktuellen Seite. Wenn es 47 Kunden gibt und man Seite 0 mit Größe 5 anfordert,
enthält `content` 5 Kunden, aber `total_elements` ist 47. Der Router braucht diese Zahl,
um ausrechnen zu können, wie viele Seiten es insgesamt gibt.

---

### 2.3 [`repository/kunde_repository.py`](../../src/kunde/repository/kunde_repository.py)

#### Imports des Repositories

```python
from collections.abc import Mapping
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from kunde.entity import Kunde
from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
```

`Mapping` aus `collections.abc` ist ein nur-lesender Dictionary-Supertyp. Der Parameter
`suchparameter` in `find()` akzeptiert damit nicht nur `dict`, sondern jeden Typ, der
wie ein Dictionary funktioniert (lesend). Das macht die Methode flexibler ohne
Einschränkungen für den Aufrufer.

`func` und `select` aus SQLAlchemy sind die Bausteine für SQL-Abfragen in Python.
`select(Kunde)` erzeugt `SELECT * FROM kunde`, `func.count()` entspricht `COUNT(*)`.

`Session` repräsentiert eine aktive Datenbankverbindung inklusive laufender Transaktion.
`joinedload` ist eine Strategie zum Laden von Beziehungen: Statt mehrere separate Abfragen
zu machen, wird ein SQL-JOIN verwendet, der Kunden und ihre verknüpften Daten in einem
einzigen Datenbankzugriff holt.

#### [`find_by_id`](../../src/kunde/repository/kunde_repository.py#L20): Frühzeitiger Ausstieg

```python
def find_by_id(self, kunde_id: int | None, session: Session) -> Kunde | None:
    logger.debug("kunde_id={}", kunde_id)

    if kunde_id is None:
        return None
```

Die Methode akzeptiert `int | None` als `kunde_id`. Das klingt zunächst merkwürdig –
warum sollte man nach einem Kunden suchen, wenn man keine ID hat? Der Grund liegt in der
Nutzung dieser Methode aus dem Service: Der Service bekommt IDs aus HTTP-Pfadparametern,
die theoretisch fehlen können. Indem die Methode `None` direkt behandelt, muss der
Aufrufer nicht erst prüfen, ob er eine echte ID hat.

`logger.debug("kunde_id={}", kunde_id)` loggt den Eingabewert für Debugging. Loguru's
Platzhalter-Syntax `{}` mit dem Wert als zweitem Argument ist schneller als f-Strings,
weil die String-Formatierung nur bei aktiviertem Debug-Level ausgeführt wird.

#### [`find_by_id`](../../src/kunde/repository/kunde_repository.py#L20): Die SQL-Abfrage

```python
    statement: Final = (
        select(Kunde)
        .options(
            joinedload(Kunde.adresse),
            joinedload(Kunde.bestellungen),
        )
        .where(Kunde.id == kunde_id)
    )
```

`select(Kunde)` ist der Startpunkt der Abfrage. Es bedeutet: "Wähle alle Spalten aus der
`kunde`-Tabelle aus." Das Ergebnis ist ein Python-Objekt, kein SQL-String. SQLAlchemy
übersetzt es erst später in echtes SQL, wenn die Abfrage ausgeführt wird.

`.options(joinedload(Kunde.adresse), joinedload(Kunde.bestellungen))` erweitert die
Abfrage. Statt `SELECT * FROM kunde WHERE id = ?` wird es zu
`SELECT * FROM kunde JOIN adresse ON ... JOIN bestellung ON ... WHERE id = ?`.
Alle benötigten Daten kommen in einer einzigen Datenbankabfrage. Ohne `joinedload` würde
SQLAlchemy beim ersten Zugriff auf `kunde.adresse` automatisch eine zweite Abfrage
auslösen – das sogenannte N+1-Problem.

`.where(Kunde.id == kunde_id)` fügt die `WHERE`-Bedingung hinzu. Das `==` ist kein
Python-Vergleich, sondern ein überladener Operator, den SQLAlchemy nutzt, um die
SQL-Bedingung zu bauen. Am Ende wird daraus `WHERE id = ?` mit einem Prepared Statement,
das SQL-Injection verhindert.

#### [`find_by_id`](../../src/kunde/repository/kunde_repository.py#L20): Ausführung

```python
    kunde: Final = session.scalar(statement)

    logger.debug("{}", kunde)
    return kunde
```

`session.scalar(statement)` führt die Abfrage aus und gibt genau ein Objekt zurück.
"Scalar" bedeutet hier: Ein einzelner Wert, nicht eine Liste. Wenn die Abfrage keinen
Treffer liefert, gibt `scalar()` `None` zurück – das ist im Rückgabetyp `Kunde | None`
ausgedrückt.

Der zweite Log-Aufruf gibt das Ergebnis aus. Da `Kunde.__repr__` definiert ist, sieht
der Log-Eintrag wie `Kunde(id=1042, nachname=Müller, email=mueller@example.de)` aus.

#### [`find`](../../src/kunde/repository/kunde_repository.py#L46): Der öffentliche Dispatcher

```python
def find(
    self,
    suchparameter: Mapping[str, str],
    pageable: Pageable,
    session: Session,
) -> Slice[Kunde]:
    if not suchparameter:
        return self._find_all(pageable=pageable, session=session)
```

`find()` ist die einzige öffentliche Such-Methode. Sie entscheidet anhand der
Suchparameter, welche private Methode aufgerufen wird. Das ist das Dispatcher-Pattern:
Eine zentrale Methode verteilt die Arbeit, die eigentliche Logik steckt in privaten Methoden.

`if not suchparameter` prüft, ob das Dictionary leer ist. Ein leeres Dictionary ist in
Python "falsy" – der `not`-Operator ergibt `True`. Wenn keine Suchparameter übergeben
wurden, sollen alle Kunden zurückgegeben werden.

#### [`find`](../../src/kunde/repository/kunde_repository.py#L46): Suche nach Typ

```python
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

Die `for`-Schleife iteriert über die Suchparameter. In der Praxis kommt immer höchstens
ein Parameter an – die Schleife ist aber offen für Erweiterungen.

Wenn der Key `"email"` ist, wird nach einem einzigen Kunden mit exakt dieser E-Mail gesucht.
Das Ergebnis wird manuell in ein `Slice` verpackt: `(kunde,)` ist ein Tupel mit einem
Element (das Komma ist zwingend!). `total_elements=1` ist korrekt, weil die E-Mail eindeutig
ist und nur ein Ergebnis möglich ist.

`return Slice(content=(), total_elements=0)` am Ende fängt unbekannte Suchparameter ab.
Statt einen Fehler zu werfen, gibt die Methode einfach ein leeres Ergebnis zurück.

#### [`_find_all`](../../src/kunde/repository/kunde_repository.py#L84): Die Paginierungs-Abfrage

```python
def _find_all(self, pageable: Pageable, session: Session) -> Slice[Kunde]:
    offset = pageable.number * pageable.size

    statement: Final = (
        (
            select(Kunde)
            .options(joinedload(Kunde.adresse), joinedload(Kunde.bestellungen))
            .limit(pageable.size)
            .offset(offset)
        )
        if pageable.size != 0
        else (
            select(Kunde)
            .options(joinedload(Kunde.adresse), joinedload(Kunde.bestellungen))
        )
    )
```

Der ternäre Ausdruck baut zwei verschiedene SQL-Statements: eines mit und eines ohne
`LIMIT`/`OFFSET`. Wenn `pageable.size == 0` ist, bedeutet das "alle Kunden ohne
Paginierung" – ein spezieller Fall für administrative Anfragen oder Tests.

Mit `LIMIT` und `OFFSET` sieht das SQL aus wie: `SELECT ... FROM kunde JOIN ... LIMIT 5 OFFSET 10`.
Das holt genau die Zeilen 11 bis 15, also die zweite Seite mit 5 Einträgen.

#### [`_find_all`](../../src/kunde/repository/kunde_repository.py#L84): Ausführung und unique()

```python
    kunden: Final = session.scalars(statement).unique().all()
    anzahl: Final = self._count_all_rows(session)
    kunde_slice: Final = Slice(content=tuple(kunden), total_elements=anzahl)
    return kunde_slice
```

`session.scalars()` gibt mehrere Objekte zurück – im Plural. `.unique()` ist bei
`joinedload` auf eine 1:N-Beziehung zwingend notwendig. Ein JOIN erzeugt mehrere
Datenbankzeilen pro Kunde, wenn der Kunde mehrere Bestellungen hat. Ohne `.unique()`
würde SQLAlchemy denselben Kunden mehrfach im Ergebnis zurückgeben – einmal pro
Bestellung. `.unique()` dedupliziert das Ergebnis, so dass jeder Kunde genau einmal
erscheint, aber mit all seinen Bestellungen befüllt.

`.all()` materialisiert das Ergebnis zu einer Python-Liste. `tuple(kunden)` konvertiert
diese Liste in ein unveränderliches Tupel, wie es das `Slice`-Dataclass erwartet.

`self._count_all_rows(session)` macht eine separate Zählanfrage, um `total_elements` zu
ermitteln. Diese zweite Abfrage ist notwendig, weil `LIMIT` die Ergebnismenge begrenzt
und wir die Gesamtzahl trotzdem brauchen.

#### [`_count_all_rows`](../../src/kunde/repository/kunde_repository.py#L114) und [`_count_rows_nachname`](../../src/kunde/repository/kunde_repository.py#L178)

```python
def _count_all_rows(self, session: Session) -> int:
    statement: Final = select(func.count()).select_from(Kunde)
    count: Final = session.execute(statement).scalar()
    return count if count is not None else 0
```

`select(func.count())` entspricht `SELECT COUNT(*)`. Das `select_from(Kunde)` sagt
SQLAlchemy, von welcher Tabelle gezählt werden soll – der ergibt dann
`SELECT COUNT(*) FROM kunde`.

`session.execute(statement).scalar()` führt die Abfrage aus und extrahiert den einzelnen
Zahlenwert. `session.scalar()` wäre hier auch möglich, aber `execute().scalar()` ist bei
reinen COUNT-Abfragen idiomatischer, weil `execute()` ein niedrigeres Level der
SQLAlchemy-API ist und `scalar()` hier den ersten Wert der ersten Zeile extrahiert.

`count if count is not None else 0` – theoretisch kann `scalar()` `None` zurückgeben,
wenn die Abfrage kein Ergebnis hat. Bei `COUNT(*)` passiert das in der Praxis nie, aber
der Rückgabetyp von SQLAlchemy ist `T | None`, und Python's Typprüfer würde ohne diesen
Fallback eine Warnung ausgeben.

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

`select(Kunde.nachname)` selektiert nur die Nachname-Spalte, nicht das gesamte
Kunden-Objekt. Das Ergebnis ist eine Liste von Strings, nicht eine Liste von `Kunde`-Objekten.

`Kunde.nachname.ilike(f"%{teil}%")` erzeugt einen case-insensitiven LIKE-Vergleich.
`ilike` ist der "case-insensitive like"-Operator – Groß- und Kleinschreibung ist egal.
Die Prozent-Zeichen `%` sind SQL-Wildcards für beliebige Zeichenfolgen: `%Müll%` findet
"Müller", "Mülleimer" und "Schmüller" gleichzeitig.

`.distinct()` entspricht dem SQL-Schlüsselwort `DISTINCT` und verhindert doppelte
Nachnamen im Ergebnis. Wenn es drei Kunden mit dem Nachnamen "Müller" gibt, erscheint
"Müller" trotzdem nur einmal in der Liste.

#### [`exists_email`](../../src/kunde/repository/kunde_repository.py#L207) und [`exists_email_other_id`](../../src/kunde/repository/kunde_repository.py#L244)

```python
def exists_email(self, email: str, session: Session) -> bool:
    statement: Final = select(func.count()).where(Kunde.email == email)
    anzahl: Final = session.scalar(statement)
    return anzahl is not None and anzahl > 0
```

Diese Methode prüft, ob eine E-Mail-Adresse bereits in der Datenbank existiert. Statt
den Kunden selbst zu laden und zu prüfen, zählt sie nur die Treffer. `COUNT(*)` ist
effizienter als `SELECT *`, weil die Datenbank keine Zeilen übertragen muss.

```python
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

`exists_email_other_id` ist die Variante für den Update-Fall. Beim Aktualisieren eines
Kunden darf er seine eigene E-Mail behalten – nur fremde E-Mails sind verboten.
`.where(Kunde.id != kunde_id)` schließt den aktuellen Kunden aus der Suche aus.

#### [`create`](../../src/kunde/repository/kunde_repository.py#L223)

```python
def create(self, kunde: Kunde, session: Session) -> Kunde:
    session.add(instance=kunde)
    session.flush(objects=[kunde])
    return kunde
```

`session.add(instance=kunde)` teilt SQLAlchemy mit, dass dieses Objekt in die Datenbank
gehört. Zu diesem Zeitpunkt passiert noch nichts in der Datenbank – das Objekt wird nur
in die "pending"-Liste der Session aufgenommen.

`session.flush(objects=[kunde])` schreibt das Objekt in die Datenbank innerhalb der
laufenden Transaktion. Es ist noch kein `commit()` – die Änderung ist noch nicht dauerhaft
und kann noch rückgängig gemacht werden. Aber der wichtige Effekt: Die Datenbank vergibt
jetzt die ID. Nach `flush()` hat `kunde.id` einen Wert, auch ohne `commit()`. Das
erlaubt es, die ID direkt im Location-Header der HTTP-Antwort zurückzugeben.

#### [`delete_by_id`](../../src/kunde/repository/kunde_repository.py#L284)

```python
def delete_by_id(self, kunde_id: int, session: Session) -> None:
    kunde: Final = self.find_by_id(kunde_id=kunde_id, session=session)
    if kunde is None:
        return

    session.delete(kunde)
    session.flush()
```

Das Löschen beginnt mit einem Laden. Das ist nötig, weil SQLAlchemy das Objekt kennen
muss, bevor es es löschen kann. `session.delete(kunde)` markiert das Objekt als
zu-löschen in der Session. Erst `session.flush()` führt das eigentliche `DELETE`-Statement
aus.

`cascade="save-update, delete"` in der `Kunde`-Entity sorgt dafür, dass beim Löschen des
Kunden automatisch auch seine Adresse und alle Bestellungen gelöscht werden. SQLAlchemy
generiert die nötigen `DELETE`-Statements für die verknüpften Tabellen selbst.

Wenn der Kunde nicht existiert (`kunde is None`), kehrt die Methode still zurück ohne
Fehler. Diese Entscheidung spiegelt das HTTP-Protokoll wider: `DELETE` ist idempotent –
mehrfaches Löschen derselben Ressource sollte dasselbe Ergebnis haben wie einmaliges
Löschen (nämlich: die Ressource ist nicht mehr da).

---

## 3. Service-Layer

Der Service enthält die Geschäftslogik. Er kennt Repository und Entities,
gibt aber nach außen nur DTOs zurück. Er ist der einzige Ort, der Datenbank-Sessions öffnet.

---

### 3.1 [`service/exceptions.py`](../../src/kunde/service/exceptions.py)

#### EmailExistsError

```python
class EmailExistsError(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Existierende Email: {email}")
        self.email = email
```

Eigene Exception-Klassen zu definieren statt `raise Exception("Fehler")` hat einen klaren
Vorteil: Der Exception-Handler im Router kann mit `except EmailExistsError` gezielt auf
diesen Fehlertyp reagieren und die passende HTTP-Antwort (422 Unprocessable Entity) zurückgeben,
ohne andere Fehlertypen zu treffen.

`super().__init__(...)` ruft den Konstruktor der Elternklasse `Exception` auf. Der String
wird die Fehlermeldung, die im Traceback erscheint und von `str(err)` zurückgegeben wird.

`self.email = email` speichert die problematische E-Mail-Adresse als Attribut. Der
Exception-Handler im Router kann damit in der HTTP-Antwort mitteilen, welche konkrete
E-Mail bereits vergeben ist.

#### NotFoundError

```python
class NotFoundError(Exception):
    def __init__(
        self,
        kunde_id: int | None = None,
        suchparameter: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__("Not Found")
        self.kunde_id = kunde_id
        self.suchparameter = suchparameter
```

Beide Parameter sind optional (`= None`). Das ist bewusste Flexibilität: Beim Suchen nach
einer ID wird `NotFoundError(kunde_id=42)` geworfen. Beim Suchen mit Filtern wird
`NotFoundError(suchparameter={"nachname": "Müller"})` geworfen. Und beim Suchen nach
Nachnamen-Strings wird `raise NotFoundError` ohne Parameter geworfen. Alle drei Fälle
werden von derselben Exception-Klasse abgedeckt.

#### VersionOutdatedError

```python
class VersionOutdatedError(Exception):
    def __init__(self, version: int) -> None:
        super().__init__(f"Veraltete Version: {version}")
        self.version = version
```

Diese Exception wird geworfen, wenn ein Client versucht, einen Kunden zu aktualisieren,
aber eine ältere Version-Nummer mitschickt als die, die in der Datenbank steht. Das deutet
darauf hin, dass jemand anderes den Kunden zwischenzeitlich verändert hat. Der Service wirft
`VersionOutdatedError`, der Router fängt ihn und antwortet mit HTTP 409 Conflict.

---

### 3.2 [`service/adresse_dto.py`](../../src/kunde/service/adresse_dto.py)

#### Was ist ein DTO?

```python
@dataclass(eq=False, slots=True, kw_only=True)
class AdresseDTO:
    plz: str
    ort: str

    @classmethod
    def from_adresse(cls, adresse: Adresse) -> "AdresseDTO":
        return cls(plz=adresse.plz, ort=adresse.ort)
```

DTO steht für Data Transfer Object – eine einfache Datenklasse ohne jegliche Datenbanklogik.
Warum nicht direkt die `Adresse`-Entity aus dem Service zurückgeben? Die Entity enthält
SQLAlchemy-interne Felder wie `kunde_id` und `id`, außerdem eine Rückreferenz auf das
`Kunde`-Objekt. Wenn diese Entity an den Router weitergegeben wird, könnte ein unvorsichtiger
Zugriff darauf eine SQL-Abfrage auslösen, wenn keine aktive Session mehr offen ist.

Das DTO ist ein sauberer Schnitt: Es enthält nur die Felder, die nach außen sichtbar sein
sollen (`plz` und `ort`). Kein `id`, kein `kunde_id`, keine Rückreferenz.

`@classmethod` bekommt die Klasse selbst als erstes Argument (`cls`). Das ermöglicht
`cls(...)` statt `AdresseDTO(...)` direkt zu schreiben – ein Vorteil für Vererbung.

`"AdresseDTO"` in Anführungszeichen ist ein Forward Reference, weil der Rückgabetyp die
eigene Klasse referenziert, die zum Zeitpunkt der Methoden-Definition noch nicht vollständig
definiert ist. Mit `from __future__ import annotations` am Anfang der Datei wären die
Anführungszeichen nicht nötig.

---

### 3.3 [`service/bestellung_dto.py`](../../src/kunde/service/bestellung_dto.py)

#### Identische Struktur, andere Felder

```python
@dataclass(eq=False, slots=True, kw_only=True)
class BestellungDTO:
    produktname: str
    menge: int

    @classmethod
    def from_bestellung(cls, bestellung: Bestellung) -> "BestellungDTO":
        return cls(produktname=bestellung.produktname, menge=bestellung.menge)
```

`BestellungDTO` ist strukturell identisch mit `AdresseDTO`. Es exportiert nur
`produktname` und `menge` – die zwei fachlich relevanten Felder. Die Datenbank-interne
`id`, die `kunde_id` und die Rückreferenz auf den Kunden werden weggelassen.

---

### 3.4 [`service/kunde_dto.py`](../../src/kunde/service/kunde_dto.py)

#### Import und Klassen-Felder

```python
from __future__ import annotations
from dataclasses import dataclass

from kunde.entity.kunde import Kunde
from kunde.service.adresse_dto import AdresseDTO
from kunde.service.bestellung_dto import BestellungDTO

@dataclass
class KundeDTO:
    id: int | None
    nachname: str
    email: str
    version: int
    adresse: AdresseDTO
    bestellungen: list[BestellungDTO]
```

`from __future__ import annotations` ersetzt hier die Anführungszeichen für Forward
References. Dank dieses Imports kann `KundeDTO` als Rückgabetyp in `from_kunde()` stehen,
ohne in Anführungszeichen geschrieben werden zu müssen.

`@dataclass` ohne Parameter verwendet Standard-Einstellungen. Im Gegensatz zu `Pageable`
und den DTOs gibt es hier kein `eq=False` oder `slots=True`. Das ist eine bewusste
Vereinfachung: `KundeDTO` ist ein einfacheres Transfer-Objekt, das keine speziellen
Performance-Anforderungen hat.

`adresse: AdresseDTO` und `bestellungen: list[BestellungDTO]` zeigen, wie DTOs
verschachtelt werden können. Das `KundeDTO` enthält keine SQLAlchemy-Entities, sondern
andere DTOs. Die Konvertierung passiert vollständig in der Factory-Methode.

#### Die Factory-Methode from_kunde

```python
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

`from_kunde` ist das zentrale Konvertierungsstück. Es nimmt eine `Kunde`-Entity aus der
Datenbank und erstellt daraus ein sauberes `KundeDTO`.

`AdresseDTO.from_adresse(kunde.adresse)` delegiert die Konvertierung der Adresse an die
zuständige Factory-Methode. Jedes DTO ist für seine eigene Konvertierung verantwortlich.

`[BestellungDTO.from_bestellung(b) for b in kunde.bestellungen]` ist eine List
Comprehension. Sie iteriert über alle Bestellungen des Kunden und konvertiert jede einzelne
in ein `BestellungDTO`. Das Ergebnis ist eine Python-Liste von DTOs.

---

### 3.5 [`service/kunde_read_service.py`](../../src/kunde/service/kunde_read_service.py)

#### Imports und Konstruktor

```python
from kunde.repository import KundeRepository, Session
from kunde.repository.pageable import Pageable
from kunde.repository.slice import Slice
from kunde.service.exceptions import NotFoundError
from kunde.service.kunde_dto import KundeDTO

class KundeReadService:
    def __init__(self, repo: KundeRepository) -> None:
        self.repo: KundeRepository = repo
```

Der Konstruktor bekommt ein `KundeRepository` übergeben. Das ist das Dependency-Injection-Muster:
Der Service erstellt das Repository nicht selbst, sondern bekommt es von außen. Das hat
einen konkreten Vorteil für Tests: Man kann dem Service ein Mock-Repository geben, das
statt echter Datenbankabfragen vordefinierte Werte zurückgibt, ohne eine Datenbank zu
benötigen.

`Session` kommt aus dem Repository-Paket, nicht von SQLAlchemy direkt. Das ist ein
vorkonfigurierter Session-Factory, der die Datenbankverbindung kennt.

#### [`KundeReadService.find_by_id`](../../src/kunde/service/kunde_read_service.py#L24): Session öffnen

```python
def find_by_id(self, kunde_id: int) -> KundeDTO:
    logger.debug("kunde_id={}", kunde_id)

    with Session() as session:
```

`with Session() as session:` öffnet eine Datenbanksession. "Session" in SQLAlchemy ist
das Konzept einer Arbeitseinheit: Sie verwaltet eine Datenbankverbindung, hält
alle geladenen Objekte im Speicher und verwaltet die laufende Transaktion.

Der `with`-Block ist ein Context Manager: Python ruft automatisch `__enter__` beim
Betreten und `__exit__` beim Verlassen auf. Bei der Session bedeutet das: Beim Verlassen
wird die Session automatisch geschlossen und alle Ressourcen werden freigegeben – auch
wenn ein Fehler aufgetreten ist.

#### [`KundeReadService.find_by_id`](../../src/kunde/service/kunde_read_service.py#L24): Walrus-Operator

```python
        if (
            kunde := self.repo.find_by_id(kunde_id=kunde_id, session=session)
        ) is None:
            message: Final = f"Kein Kunde mit der ID {kunde_id}"
            logger.debug("NotFoundError: {}", message)
            raise NotFoundError(kunde_id=kunde_id)
```

`:=` ist der Walrus-Operator, eingeführt in Python 3.8. Er weist das Ergebnis der rechten
Seite der Variable auf der linken Seite zu und gibt diesen Wert gleichzeitig zurück.

Diese zwei Zeilen ohne Walrus-Operator wären:

```python
kunde = self.repo.find_by_id(kunde_id=kunde_id, session=session)
if kunde is None:
```

Mit dem Walrus-Operator passiert beides in einem einzigen Ausdruck: Das Repository wird
aufgerufen, das Ergebnis wird in `kunde` gespeichert, und gleichzeitig wird geprüft ob
es `None` ist. Das spart eine Zeile und hält die Logik kompakt.

`raise NotFoundError(kunde_id=kunde_id)` – wenn kein Kunde gefunden wurde, wird eine
Exception geworfen. Diese Exception wandert den Call-Stack hinauf bis zu FastAPI, das
einen registrierten Exception-Handler aufruft und HTTP 404 zurückgibt.

#### [`KundeReadService.find_by_id`](../../src/kunde/service/kunde_read_service.py#L24): Konvertierung und Commit

```python
        kunde_dto: Final = KundeDTO.from_kunde(kunde)
        session.commit()

    logger.debug("{}", kunde_dto)
    return kunde_dto
```

`KundeDTO.from_kunde(kunde)` passiert noch innerhalb des `with`-Blocks, weil die Session
zu diesem Zeitpunkt noch offen sein muss. Das `KundeDTO` greift auf `kunde.adresse` und
`kunde.bestellungen` zu – falls diese noch nicht geladen wären (was bei `joinedload`
nicht der Fall ist), würde SQLAlchemy eine aktive Session brauchen.

`session.commit()` schließt die Transaktion erfolgreich ab. Bei reinen Leseoperationen
ist das technisch nicht zwingend erforderlich, aber es ist Best Practice: Es signalisiert
der Datenbank, dass die Transaktion abgeschlossen ist und alle gehaltenen Sperren freigegeben
werden können.

Nach dem `with`-Block ist die Session geschlossen. Das `kunde_dto` enthält nur Python-Objekte
ohne Datenbankverbindung – es kann sicher an den Router weitergegeben werden.

#### [`find`](../../src/kunde/service/kunde_read_service.py#L47): Suche mit Parametern

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
```

`find()` nimmt keine Session als Parameter entgegen – im Gegensatz zum Repository.
Der Service ist der einzige Ort, der Sessions erstellt und verwaltet. Das Repository
bekommt die Session übergeben, weil es keine Sessions erstellen soll.

Wenn das Repository ein leeres `Slice` zurückgibt (`len(kunde_slice.content) == 0`), ist
das aus fachlicher Sicht ein Fehler: Der Client hat nach Kunden gesucht, die nicht existieren.
`NotFoundError(suchparameter=suchparameter)` – hier wird der Parameter mitgegeben, damit
der Exception-Handler im Router die Fehlermeldung anreichern kann.

#### [`find`](../../src/kunde/service/kunde_read_service.py#L47): Konvertierung der Ergebnisse

```python
        kunden_dto: Final = tuple(
            KundeDTO.from_kunde(kunde) for kunde in kunde_slice.content
        )
        session.commit()

    kunden_dto_slice = Slice(
        content=kunden_dto, total_elements=kunde_slice.total_elements
    )
    return kunden_dto_slice
```

`tuple(KundeDTO.from_kunde(kunde) for kunde in kunde_slice.content)` ist ein Generator-Ausdruck.
Im Gegensatz zu einer List Comprehension `[... for ...]` erzeugt ein Generator-Ausdruck
keine Zwischenliste im Speicher. `tuple(...)` materialisiert den Generator direkt als Tupel.
Das ist geringfügig effizienter als erst eine Liste und dann ein Tupel zu erstellen.

Das neue `Slice`-Objekt entsteht außerhalb des `with`-Blocks. Das ist möglich, weil
`kunden_dto` ein Tupel von reinen Python-Objekten ist, das keine SQLAlchemy-Session mehr
benötigt. `total_elements` wird direkt vom Repository-Slice übernommen.

#### [`find_nachnamen`](../../src/kunde/service/kunde_read_service.py#L81)

```python
def find_nachnamen(self, teil: str) -> Sequence[str]:
    with Session() as session:
        nachnamen: Final = self.repo.find_nachnamen(teil=teil, session=session)
        session.commit()

    if len(nachnamen) == 0:
        raise NotFoundError
    return nachnamen
```

`Sequence[str]` ist ein schreibgeschützter Supertyp für `list[str]`. Der Aufrufer kann
den Inhalt lesen, aber nicht verändern. Es ist eine schwächere Garantie als `tuple`, aber
stärker als `list`.

`raise NotFoundError` – hier wird die Exception ohne Argumente geworfen. Die `NotFoundError`-Klasse
hat beide Parameter als optional definiert, sodass das möglich ist. Dieser Fall tritt auf,
wenn der Teilstring nicht in einem einzigen Nachnamen vorkommt.

---

## 4. Router-Layer

Der Router empfängt HTTP-Requests, ruft den Service auf und gibt HTTP-Antworten zurück.
Er enthält keine Geschäftslogik – nur HTTP-Protokoll-Details wie Status-Codes und Header.

---

### 4.1 [`router/constants.py`](../../src/kunde/router/constants.py)

#### HTTP-Header als benannte Konstanten

```python
from typing import Final

ETAG: Final = "ETag"
IF_MATCH: Final = "if-match"
IF_MATCH_MIN_LEN: Final = 3
IF_NONE_MATCH: Final = "If-None-Match"
IF_NONE_MATCH_MIN_LEN: Final = 3
```

Statt überall `"ETag"` oder `"If-None-Match"` als sogenannte "Magic Strings" hardzucoden,
werden die Werte einmal benannt und in einer zentralen Datei definiert.

Der praktische Vorteil ist schnell erklärt: Wenn jemand aus Versehen `"ETags"` statt
`"ETag"` schreibt, gibt es keinen Fehler – den String akzeptiert Python stillschweigend.
Wenn aber `ETAG` falsch geschrieben wird (etwa als `ETGAS`), gibt es sofort einen
`NameError` beim Import, der auffällt.

`IF_NONE_MATCH_MIN_LEN: Final = 3` – ein gültiger ETag-Wert ist zum Beispiel `"0"`:
ein Anführungszeichen, eine Ziffer, ein Anführungszeichen. Das ergibt Länge 3. Die
Mindestlänge 3 sichert, dass der Wert syntaktisch korrekt ist – ein `"` allein mit
Länge 1 wäre kein gültiger ETag.

ETag ist ein HTTP-Caching-Mechanismus: Der Server schickt den ETag-Header mit jeder
Antwort, der Client speichert diesen Wert und schickt ihn beim nächsten Request als
`If-None-Match` zurück. Der Server vergleicht die Versionen und antwortet mit 304 Not
Modified, wenn sich nichts geändert hat – spart Bandbreite und Zeit.

---

### 4.2 [`router/page.py`](../../src/kunde/router/page.py)

#### Die Page-Klasse als API-Antwort

```python
@dataclass
class Page:
    content: tuple[dict[str, Any], ...]
    page_number: int
    page_size: int
    total_elements: int
    total_pages: int
```

Warum existiert `Page` neben `Slice`? `Slice` enthält die Entities oder DTOs aus dem
Repository – Python-Objekte. `Page` enthält serialisierte Dictionaries, die direkt in
JSON umgewandelt werden können, plus die Paginierungsmetadaten, die der API-Nutzer braucht.

`content: tuple[dict[str, Any], ...]` ist ein Tupel von Dictionaries. `dict[str, Any]`
bedeutet: jeder Schlüssel ist ein String, jeder Wert kann beliebigen Typ haben. JSON-kompatibel.

Die Felder `page_number`, `page_size`, `total_elements` und `total_pages` sind
Metadaten, die dem Client helfen, die Paginierung zu verstehen: Wie viele Seiten gibt es?
Auf welcher bin ich? Wie viele Einträge insgesamt?

#### Die Berechnung der Seitenanzahl

```python
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

`(total_elements + pageable.size - 1) // pageable.size` ist die Standard-Formel für
Aufrunden mit ganzzahliger Division. Reguläre Division von 14 durch 5 ergibt 2.8 – es
gibt also 3 Seiten. Die Formel rechnet: `(14 + 4) // 5 = 18 // 5 = 3`. Korrekt.

`max(1, ...)` stellt sicher, dass es immer mindestens eine Seite gibt, auch wenn die
Datenbank leer ist (`total_elements = 0` würde sonst `0 // 5 = 0` ergeben).

---

### 4.3 [`router/kunde_read_router.py`](../../src/kunde/router/kunde_read_router.py)

#### Imports und Router-Instanz

```python
from dataclasses import asdict
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse

from kunde.router.dependencies import get_read_service
from kunde.service import KundeReadService

kunde_read_router: Final = APIRouter(tags=["Lesen"])
```

`APIRouter` ist das FastAPI-Konzept für modulare Routen-Gruppen. Statt alle Endpunkte
direkt an die Haupt-App zu hängen, werden sie in einem Router gesammelt. Der Router wird
dann in `fastapi_app.py` mit einem Präfix eingebunden: `app.include_router(kunde_read_router, prefix="/rest/kunden")`.
Jede Route im Router bekommt diesen Präfix automatisch vorangestellt.

`tags=["Lesen"]` gruppiert alle Endpunkte dieses Routers in der automatisch generierten
Swagger-Dokumentation unter der Überschrift "Lesen".

`asdict` aus `dataclasses` konvertiert ein Dataclass-Objekt rekursiv in ein Dictionary.

#### [`get_by_id`](../../src/kunde/router/kunde_read_router.py#L24): Signatur und Decorator

```python
@kunde_read_router.get("/{kunde_id}")
def get_by_id(
    kunde_id: int,
    request: Request,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> Response:
    kunde: Final = service.find_by_id(kunde_id=kunde_id)
```

`@kunde_read_router.get("/{kunde_id}")` registriert diese Funktion für HTTP GET-Anfragen
an `/rest/kunden/{kunde_id}`. Die geschweifte Klammern `{kunde_id}` ist ein Pfadparameter,
den FastAPI automatisch aus der URL extrahiert. Das Beste: FastAPI konvertiert den String
automatisch in den deklarierten Typ – hier `int`. Wenn jemand `GET /rest/kunden/abc`
aufruft, antwortet FastAPI mit HTTP 422, bevor der Handler aufgerufen wird.

`service: Annotated[KundeReadService, Depends(get_read_service)]` ist FastAPIs
Dependency-Injection-Mechanismus. `Depends(get_read_service)` sagt FastAPI: "Ruf die
Funktion `get_read_service()` auf und übergib das Ergebnis als `service`-Parameter."
`Annotated[..., ...]` ist Standard-Python für einen Typ mit Metadaten – die Metadaten
hier sind die FastAPI-Anweisung für Dependency Injection.

#### [`get_by_id`](../../src/kunde/router/kunde_read_router.py#L24): ETag-Prüfung

```python
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
```

`request.headers.get(IF_NONE_MATCH)` liest den `If-None-Match`-Header aus dem Request.
`get()` gibt `None` zurück, wenn der Header nicht gesetzt ist.

Die mehrzeilige `if`-Bedingung prüft drei Dinge: Erstens, ob der Header überhaupt vorhanden
ist. Zweitens, ob er die Mindestlänge hat. Drittens, ob er in Anführungszeichen eingeschlossen
ist (gültiges ETag-Format ist immer `"version"`).

`if_none_match[1:-1]` schneidet das erste und letzte Zeichen ab: `'"42"'` wird zu `'42'`.
`int(version)` konvertiert den String zu einer Zahl. Der `try`/`except ValueError` fängt
den Fall ab, dass der Wert keine gültige Zahl ist (zum Beispiel `'"abc"'` statt `'"42"'`).

Wenn Version stimmt: HTTP 304 Not Modified – kein Body, der Client nutzt seinen Cache.

#### [`get_by_id`](../../src/kunde/router/kunde_read_router.py#L24): Antwort mit ETag

```python
    return JSONResponse(
        content=_kunde_to_dict(kunde),
        headers={ETAG: f'"{kunde.version}"'},
    )
```

`JSONResponse` serialisiert das Dictionary zu JSON und setzt den Content-Type-Header
auf `application/json`. `_kunde_to_dict(kunde)` konvertiert das `KundeDTO` in ein
JSON-kompatibles Dictionary.

`headers={ETAG: f'"{kunde.version}"'}` setzt den ETag-Header. Der Wert ist die aktuelle
Version in Anführungszeichen: `"0"` oder `"42"`. Bei der nächsten Anfrage schickt der
Client diesen Wert als `If-None-Match` und bekommt bei unverändertem Kunden 304 zurück.

#### [`get`](../../src/kunde/router/kunde_read_router.py#L65): Query-Parameter verarbeiten

```python
@kunde_read_router.get("")
def get(
    request: Request,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> JSONResponse:
    query_params: Final = request.query_params

    page: Final = query_params.get("page")
    size: Final = query_params.get("size")
    pageable: Final = Pageable.create(number=page, size=size)
```

`@kunde_read_router.get("")` registriert den Handler für `GET /rest/kunden` ohne weiteren Pfad.

`request.query_params` enthält alle Query-Parameter als Dictionary-ähnliches Objekt.
Bei der URL `/rest/kunden?nachname=Müller&page=0&size=5` enthält es
`{"nachname": "Müller", "page": "0", "size": "5"}`.

`Pageable.create(number=page, size=size)` validiert und konvertiert die Strings `"0"` und
`"5"` zu ganzzahligen `Pageable`-Feldern – das `create()`-Methode kümmert sich um
ungültige Werte und gibt sinnvolle Defaults zurück.

#### [`get`](../../src/kunde/router/kunde_read_router.py#L65): Suchparameter filtern und suchen

```python
    suchparameter = dict(query_params)
    suchparameter.pop("page", None)
    suchparameter.pop("size", None)

    kunde_slice: Final = service.find(suchparameter=suchparameter, pageable=pageable)

    result: Final = _kunde_slice_to_page(kunde_slice, pageable)
    return JSONResponse(content=result)
```

`dict(query_params)` erstellt eine veränderliche Kopie der Query-Parameter. Die Kopie ist
nötig, weil `query_params` selbst unveränderlich ist und kein `pop()` unterstützt.

`suchparameter.pop("page", None)` entfernt `page` aus dem Dictionary. Der zweite Parameter
`None` ist der Default-Wert, der zurückgegeben wird, wenn `page` nicht im Dictionary ist –
so gibt es keinen `KeyError`. Das ist wichtig, weil `page` und `size` keine Suchparameter
sind, sondern Paginierungsparameter. Das Repository würde nicht wissen, was es mit
`key="page"` anfangen soll.

`_kunde_slice_to_page` konvertiert das Service-Ergebnis zu einer `Page` mit Metadaten
und serialisiert sie zu einem Dictionary.

#### [`get_nachnamen`](../../src/kunde/router/kunde_read_router.py#L96)

```python
@kunde_read_router.get("/nachnamen/{teil}")
def get_nachnamen(
    teil: str,
    service: Annotated[KundeReadService, Depends(get_read_service)],
) -> JSONResponse:
    nachnamen: Final = service.find_nachnamen(teil=teil)
    return JSONResponse(content=nachnamen)
```

Dieser Endpunkt ist der einfachste im Router: Ein Teilstring aus dem URL-Pfad, ein
Service-Aufruf, eine JSON-Antwort. `nachnamen` ist eine Liste von Strings – JSON kann
das direkt serialisieren, kein manuelles Dictionary-Konvertieren nötig.

#### [Hilfsfunktionen](../../src/kunde/router/kunde_read_router.py#L113): Serialisierung

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
```

`_kunde_slice_to_page` ist eine private Hilfsfunktion – der führende Unterstrich `_`
signalisiert das. Sie nimmt ein `Slice[KundeDTO]` und ein `Pageable` und baut daraus
ein serialisiertes Dictionary mit allen Paginierungsmetadaten.

`asdict(obj=page)` aus `dataclasses` konvertiert das `Page`-Dataclass rekursiv in ein
Dictionary. Das Tupel `content` wird dabei automatisch in eine JSON-Liste umgewandelt.

```python
def _kunde_to_dict(kunde: KundeDTO) -> dict[str, Any]:
    return {
        "id": kunde.id,
        "nachname": kunde.nachname,
        "email": kunde.email,
        "adresse": {"plz": kunde.adresse.plz, "ort": kunde.adresse.ort},
        "bestellungen": [
            {"produktname": b.produktname, "menge": b.menge}
            for b in kunde.bestellungen
        ],
    }
```

`_kunde_to_dict` kontrolliert exakt, welche Felder in der JSON-Antwort erscheinen.
Das ist wichtig, weil die API eine definierte Schnittstelle nach außen hat: Nur die
hier aufgelisteten Felder werden zurückgegeben. Interne Felder wie `version` können
selektiv ein- oder ausgeschlossen werden.

---

## 5. App

### 5.1 [`fastapi_app.py`](../../src/kunde/fastapi_app.py)

#### Imports

```python
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from time import time
from typing import Final

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from loguru import logger
```

`AsyncGenerator` ist der Typ für asynchrone Generator-Funktionen – wird für die
`lifespan`-Funktion gebraucht. `asynccontextmanager` ist ein Decorator, der eine
async-Generatorfunktion in einen Context Manager verwandelt.

`GZipMiddleware` komprimiert HTTP-Antworten automatisch mit GZip-Algorithmus. Große
JSON-Antworten (Kundenlisten) können dadurch deutlich kleiner werden.

`time` aus der Standardbibliothek liefert die aktuelle Zeit als Gleitkommazahl in
Sekunden – wird für die Zeitmessung in der Response-Time-Middleware gebraucht.

#### [Lifespan](../../src/kunde/fastapi_app.py#L34): Start und Shutdown

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

`lifespan` definiert, was beim Serverstart und beim Shutdown passiert. Die Funktion ist
ein async-Generator: alles vor `yield` läuft beim Start, alles nach `yield` beim Shutdown.

`if dev_db_populate: db_populate()` befüllt die Datenbank mit Testdaten, aber nur wenn
der Dev-Modus aktiv ist. In Produktion hat `dev_db_populate` den Wert `False`, und die
Datenbank bleibt leer.

`banner(app.routes)` gibt beim Start alle registrierten Routen in der Konsole aus. Das
hilft beim Entwickeln zu sehen, welche Endpunkte verfügbar sind.

Nach dem `yield`: `engine.dispose()` schließt alle aktiven Datenbankverbindungen sauber.
Ohne diesen Aufruf würden Verbindungen offen bleiben, bis der Prozess beendet wird.

#### Die App-Instanz

```python
app: Final = FastAPI(lifespan=lifespan)
```

Diese eine Zeile erstellt die gesamte FastAPI-Applikation. `lifespan=lifespan` verbindet
die zuvor definierte Lebenszyklus-Funktion mit der App. FastAPI ruft `lifespan` beim
Serverstart auf und wartet auf das `yield`, dann wird die App gestartet. Beim Shutdown
läuft der Rest der Funktion durch.

#### [Middleware](../../src/kunde/fastapi_app.py#L51): GZip und Request-Logging

```python
app.add_middleware(GZipMiddleware, minimum_size=500)
```

`minimum_size=500` bedeutet: Antworten werden nur komprimiert, wenn sie mindestens 500
Bytes groß sind. Kleinere Antworten würden durch die Komprimierung sogar größer werden,
weil der GZip-Header selbst Platz benötigt.

```python
@app.middleware("http")
async def log_request(request: Request, call_next: ...) -> Response:
    logger.debug(f"{request.method} '{request.url}'")
    return await call_next(request)
```

Jeder HTTP-Request durchläuft diese Middleware, bevor er den eigentlichen Handler erreicht.
`call_next(request)` gibt den Request weiter – entweder an die nächste Middleware oder
direkt zum Handler. `await` ist nötig, weil FastAPI asynchron arbeitet.

#### [Middleware](../../src/kunde/fastapi_app.py#L51): Zeitmessung

```python
@app.middleware("http")
async def log_response_time(request: Request, call_next: ...) -> Response:
    start = time()
    response = await call_next(request)
    duration_ms = (time() - start) * 1000
    logger.debug("Antwortzeit: {:.2f} ms", duration_ms)
    return response
```

`start = time()` speichert den Zeitstempel vor der Verarbeitung. Nach `call_next(request)` –
wenn die Antwort fertig ist – wird die vergangene Zeit berechnet: `(time() - start) * 1000`
konvertiert Sekunden in Millisekunden. `{:.2f}` formatiert die Zahl auf zwei Nachkommastellen.

#### [Router einbinden](../../src/kunde/fastapi_app.py#L91)

```python
app.include_router(kunde_read_router, prefix="/rest/kunden")
app.include_router(kunde_write_router, prefix="/rest")

if dev_db_populate:
    app.include_router(db_populate_router, prefix="/dev")
```

`include_router` verbindet einen Router mit der App und setzt einen Präfix. Der
`kunde_read_router` mit `prefix="/rest/kunden"` macht aus `get("/{kunde_id}")` die Route
`GET /rest/kunden/{kunde_id}`. Der Präfix wird vor alle Routen des Routers gestellt.

Der Dev-Router wird nur aktiviert, wenn `dev_db_populate=True` ist. Das ist eine einfache
aber effektive Sicherheitsmaßnahme: Endpunkte für das Befüllen der Datenbank sind in
Produktion überhaupt nicht registriert und können nicht aufgerufen werden.

#### [Exception-Handler](../../src/kunde/fastapi_app.py#L125)

```python
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, _err: NotFoundError) -> Response:
    return create_problem_details(status_code=status.HTTP_404_NOT_FOUND)

@app.exception_handler(EmailExistsError)
def email_exists_error_handler(_request: Request, err: EmailExistsError) -> Response:
    return create_problem_details(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(err),
    )
```

`@app.exception_handler(NotFoundError)` registriert eine Funktion, die aufgerufen wird,
wenn irgendwo im Code eine `NotFoundError`-Exception geworfen wird. FastAPI fängt sie
automatisch ab – kein `try`/`except` in jedem Handler nötig.

`_request` und `_err` beginnen mit Unterstrich – das ist Python-Konvention für unbenutzte
Parameter. Bei `not_found_error_handler` braucht man weder den Request noch die Exception
selbst, um die Antwort zu bauen. Bei `email_exists_error_handler` wird `err` gebraucht:
`str(err)` gibt die Fehlermeldung aus dem `super().__init__(...)` zurück – also
`"Existierende Email: mueller@example.de"`.

`create_problem_details` erzeugt eine RFC 7807-konforme Fehlerantwort. RFC 7807 ist ein
Internetstandard für strukturierte Fehlermeldungen in REST-APIs: Der Body ist ein JSON-Objekt
mit definierten Feldern wie `type`, `title`, `status` und `detail`.

---

## Zusammenfassung: Datenfluss bei GET /rest/kunden/1

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

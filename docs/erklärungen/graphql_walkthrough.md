# GraphQL-Walkthrough: Kundenverwaltung

Dieses Dokument erklärt die GraphQL-Schnittstelle des Projekts – Block für Block, Zeile für Zeile.
GraphQL ist ein alternatives API-Protokoll zu REST. Statt mehrerer Endpunkte gibt es einen
einzigen Endpunkt, über den der Client selbst bestimmt, welche Felder er in der Antwort braucht.

Disclaimer: Diese Erklärung ist von Claude Code generiert worden.

---

## Inhaltsverzeichnis

1. [Architektur-Überblick](#1-architektur-überblick)
2. [graphql\_api/\_\_init\_\_.py](#2-graphql_api__init__py)
3. [graphql\_api/graphql\_types.py](#3-graphql_apigraphql_typespy)
   - [Suchparameter](#31-suchparameter)
   - [AdresseInput](#32-adresseinput)
   - [KundeInput](#33-kundeinput)
   - [AdresseType](#34-adressetype)
   - [BestellungType](#35-bestellungtype)
   - [KundeType](#36-kundetype)
   - [CreatePayload](#37-createpayload)
4. [graphql\_api/schema.py](#4-graphql_apischemapy)
   - [Service-Instanzen](#41-service-instanzen)
   - [\_to\_kunde\_type](#42-_to_kunde_type)
   - [Query.kunde](#43-querykunde)
   - [Query.kunden](#44-querykunden)
   - [Mutation.create](#45-mutationcreate)
   - [Schema und Router](#46-schema-und-router)

---

## 1. Architektur-Überblick

```text
GraphQL Request  POST /graphql
    │
    ▼
┌─────────────────┐
│  GraphQLRouter  │  nimmt den Request entgegen, parst die Query
│  (Strawberry)   │  und leitet sie an den richtigen Resolver weiter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query/Mutation │  Resolver-Methoden: lesen oder schreiben
│  (schema.py)    │  delegieren an den jeweiligen Service
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ReadService /   │  gleiche Geschäftslogik wie bei REST –
│ WriteService    │  GraphQL ist nur eine andere Transportschicht
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repository     │  SQL-Abfragen, wie gehabt
└─────────────────┘
```

Der wesentliche Unterschied zu REST: Während bei REST jede Route eine eigene Funktion
mit eigenem Rückgabeformat hat, gibt es bei GraphQL genau eine Route (`/graphql`).
Der Client schickt eine Abfrage als Text, in der er selbst angibt, welche Felder er
haben möchte. Strawberry übersetzt diese Abfrage in Methodenaufrufe auf den
Resolver-Klassen `Query` und `Mutation`.

---

## 2. [`graphql_api/__init__.py`](../../src/kunde/graphql_api/__init__.py)

#### Paketdefinition und öffentliche Exporte

```python
"""Öffentliche Schnittstelle des graphql_api-Pakets."""

from kunde.graphql_api.graphql_types import (
    AdresseInput,
    AdresseType,
    BestellungType,
    CreatePayload,
    KundeInput,
    KundeType,
    Suchparameter,
)
from kunde.graphql_api.schema import Mutation, Query, graphql_router
```

Diese Datei macht das Verzeichnis `graphql_api` zu einem Python-Paket und legt fest, welche
Namen nach außen sichtbar sind. Alle Typen aus `graphql_types.py` sowie die Resolver-Klassen
und der fertige Router aus `schema.py` werden hier gebündelt.

Das hat einen praktischen Grund: Code, der den GraphQL-Router einbinden will, schreibt
`from kunde.graphql_api import graphql_router` statt den vollständigen Pfad
`from kunde.graphql_api.schema import graphql_router` zu kennen. Die interne
Dateistruktur des Pakets bleibt ein Implementierungsdetail.

---

## 3. [`graphql_api/graphql_types.py`](../../src/kunde/graphql_api/graphql_types.py)

Diese Datei definiert alle Datentypen der GraphQL-Schnittstelle. In Strawberry gibt es
zwei Kategorien: Input-Typen (was der Client schickt) und Output-Typen (was der Server
zurückgibt). Sie sind bewusst getrennt, weil Eingabe und Ausgabe unterschiedliche
Anforderungen haben – eine Eingabe braucht zum Beispiel keine `id`, weil die erst von
der Datenbank vergeben wird.

#### Das Modul-Grundgerüst

```python
"""Strawberry-Typen für die GraphQL-API der Kundenverwaltung."""

import strawberry
```

Das einzige Import ist `strawberry`, die Bibliothek, die Python-Klassen in ein GraphQL-Schema
übersetzt. Strawberry arbeitet mit Dekoratoren: Ein `@strawberry.type` oben an einer Klasse
genügt, damit Strawberry diese Klasse ins Schema aufnimmt. Kein SDL (Schema Definition Language)
ist nötig – das Schema entsteht direkt aus dem Python-Code.

---

### 3.1 [`Suchparameter`](../../src/kunde/graphql_api/graphql_types.py#L16)

#### Eingabe für Filterabfragen

```python
@strawberry.input
class Suchparameter:
    """Filterkriterien, mit denen Kunden gesucht werden können."""

    nachname: str | None = None
    email: str | None = None
```

`@strawberry.input` kennzeichnet diese Klasse als GraphQL-Input-Typ. Ein Input-Typ
kann nur als Argument in einer Query oder Mutation verwendet werden, nie als
Rückgabewert. Das ist eine GraphQL-Regel, keine Python-Regel.

Beide Felder sind optional (`str | None = None`). Das ermöglicht flexible Suchen:
Der Client kann nur `nachname`, nur `email` oder beide zusammen übergeben.
Lässt er ein Feld weg, kommt `None` an.

---

### 3.2 [`AdresseInput`](../../src/kunde/graphql_api/graphql_types.py#L27)

#### Adresse als Eingabe beim Anlegen

```python
@strawberry.input
class AdresseInput:
    strasse: str
    hausnummer: str
    plz: str
    ort: str
```

Alle vier Felder sind Pflichtfelder ohne Default-Wert. Fehlt eines davon in der
Anfrage des Clients, lehnt Strawberry die Anfrage bereits vor dem Aufruf des
Resolvers ab – der Server bekommt eine ungültige Anfrage erst gar nicht zu sehen.

Diese Klasse entspricht inhaltlich dem `AdresseModel` in Pydantic, das für die
REST-Schnittstelle verwendet wird. Sie existiert trotzdem separat, weil GraphQL-Typen
und Pydantic-Modelle unterschiedliche Grundklassen haben und nicht geteilt werden können.

---

### 3.3 [`KundeInput`](../../src/kunde/graphql_api/graphql_types.py#L44)

#### Kundendaten als Eingabe

```python
@strawberry.input
class KundeInput:
    nachname: str
    email: str
    adresse: AdresseInput
```

`KundeInput` fasst die Pflichtfelder zusammen, die beim Anlegen eines Kunden nötig sind.
Das Feld `adresse` ist vom Typ `AdresseInput` – ein Input-Typ kann also andere Input-Typen
als Felder enthalten. Strawberry baut daraus automatisch eine verschachtelte Struktur im Schema.

Bestellungen werden beim Anlegen nicht mitgegeben, weil Bestellungen im Datenmodell
separat über eigene Vorgänge entstehen.

---

### 3.4 [`AdresseType`](../../src/kunde/graphql_api/graphql_types.py#L58)

#### Adresse als Ausgabe

```python
@strawberry.type
class AdresseType:
    strasse: str
    hausnummer: str
    plz: str
    ort: str
```

`@strawberry.type` statt `@strawberry.input` – das ist der entscheidende Unterschied.
Output-Typen (`@strawberry.type`) werden als Antwort zurückgegeben. Der Client kann
bei einer GraphQL-Abfrage gezielt auswählen, welche dieser vier Felder er braucht.
Fragt er nur `plz` und `ort` ab, überträgt der Server nur diese beiden Felder.
Das ist der Kern des GraphQL-Versprechens: kein Over-Fetching.

---

### 3.5 [`BestellungType`](../../src/kunde/graphql_api/graphql_types.py#L68)

#### Bestellung als Ausgabe

```python
@strawberry.type
class BestellungType:
    produktname: str
    menge: int
```

Ein minimaler Output-Typ mit genau den zwei Feldern, die das Datenmodell einer
Bestellung ausmachen. Felder wie `id` oder `kunde_id` werden hier nicht exponiert,
weil sie für einen Client der GraphQL-API keine Relevanz haben.

---

### 3.6 [`KundeType`](../../src/kunde/graphql_api/graphql_types.py#L76)

#### Vollständiger Kundendatensatz als Ausgabe

```python
@strawberry.type
class KundeType:
    id: int | None
    nachname: str
    email: str
    version: int
    adresse: AdresseType
    bestellungen: list[BestellungType]
```

`KundeType` ist der zentrale Ausgabe-Typ. Er enthält alle Informationen, die ein
Client über einen Kunden abfragen kann. Das Feld `adresse` verweist auf `AdresseType`
und `bestellungen` auf eine Liste von `BestellungType` – Strawberry baut daraus
automatisch ein geschachteltes GraphQL-Schema.

`id` ist `int | None`, weil ein frisch erzeugtes Objekt im Arbeitsspeicher
theoretisch noch keine ID haben kann. In der Praxis wird `KundeType` immer aus einem
`KundeDTO` gebaut, das bereits eine ID trägt.

---

### 3.7 [`CreatePayload`](../../src/kunde/graphql_api/graphql_types.py#L88)

#### Rückgabe der create-Mutation

```python
@strawberry.type
class CreatePayload:
    """Rückgabewert der create-Mutation mit der vergebenen Kunden-ID."""

    id: int
```

Mutations geben üblicherweise nicht den gesamten neu angelegten Datensatz zurück,
sondern ein schlankes Payload-Objekt. Hier reicht die vergebene ID, damit der Client
weiß, unter welcher ID er den neuen Kunden abfragen kann. Wer mehr Details braucht,
führt danach eine separate Query mit dieser ID durch.

---

## 4. [`graphql_api/schema.py`](../../src/kunde/graphql_api/schema.py)

Diese Datei verbindet alle Teile: Sie importiert die Typen, instanziiert die Services,
definiert die Resolver-Methoden und baut am Ende den fertigen Router zusammen, den
FastAPI einbinden kann.

#### Imports

```python
from collections.abc import Sequence
from typing import Final

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
```

`Sequence` wird als Rückgabetyp der `kunden`-Query gebraucht. `Final` verhindert,
dass die Modul-Level-Variablen (Services, Schema, Router) nachträglich überschrieben
werden. `GraphQLRouter` ist Strawberrys fertiger FastAPI-Router, der den `/graphql`-Endpunkt
bereitstellt.

`Info` aus `strawberry.types` wird in diesem Projekt nicht aktiv genutzt, ist aber
der übliche Weg, um in Resolvern an den Request-Kontext zu gelangen – zum Beispiel
für Header-Auswertung oder Authentifizierung.

---

### 4.1 Service-Instanzen

#### [`Modul-Level-Initialisierung`](../../src/kunde/graphql_api/schema.py#L32)

```python
_repo: Final = KundeRepository()
_read_service: Final = KundeReadService(repo=_repo)
_write_service: Final = KundeWriteService(repo=_repo)
```

Alle drei Objekte werden einmal beim Modulstart erzeugt und dann für alle eingehenden
Requests wiederverwendet. Das ist möglich, weil keines dieser Objekte Request-spezifischen
Zustand speichert – die eigentliche Datenbankverbindung wird erst in der jeweiligen
Methode über `Session()` geöffnet.

Beide Services teilen sich dasselbe Repository-Objekt. Das Repository selbst ist zustandslos
und kann bedenkenlos geteilt werden.

---

### 4.2 [`_to_kunde_type`](../../src/kunde/graphql_api/schema.py#L37)

#### Hilfsfunktion: DTO → GraphQL-Typ

```python
def _to_kunde_type(dto) -> KundeType:
    return KundeType(
        id=dto.id,
        nachname=dto.nachname,
        email=dto.email,
        version=dto.version,
        adresse=AdresseType(
            strasse=dto.adresse.strasse,
```

```python
            hausnummer=dto.adresse.hausnummer,
            plz=dto.adresse.plz,
            ort=dto.adresse.ort,
        ),
        bestellungen=[
            BestellungType(produktname=b.produktname, menge=b.menge)
            for b in dto.bestellungen
        ],
    )
```

Diese Funktion übersetzt ein `KundeDTO` in einen `KundeType`. Der Grund dafür, dass
diese Übersetzung nötig ist: Das `KundeDTO` kennt Strawberry nicht, und `KundeType`
kennt die Datenbankschicht nicht. Beide Typen existieren in unterschiedlichen Schichten
mit unterschiedlichen Verantwortlichkeiten.

Die Funktion beginnt mit einem Unterstrich (`_to_kunde_type`), was in Python die Konvention
für paket-intern verwendete Hilfsfunktionen ist. Sie taucht nicht in `__all__` auf und ist
nicht als Teil der öffentlichen API gedacht.

Das `dto.bestellungen` wird per List Comprehension Stück für Stück umgebaut. Jede
`BestellungDTO`-Instanz wird in ein `BestellungType`-Objekt überführt.

---

### 4.3 [`Query.kunde`](../../src/kunde/graphql_api/schema.py#L61)

#### Resolver für eine einzelne ID-Abfrage

```python
@strawberry.field
def kunde(self, kunde_id: strawberry.ID) -> KundeType | None:
    logger.debug("kunde_id={}", kunde_id)

    try:
        kunde_dto = _read_service.find_by_id(kunde_id=int(kunde_id))
    except NotFoundError:
        return None

    return _to_kunde_type(kunde_dto)
```

`@strawberry.field` macht diese Methode zu einem GraphQL-Feld in der `Query`-Klasse.
Aus Sicht des GraphQL-Schemas ist das ein Feld namens `kunde`, das einen `ID`-Parameter
erwartet und einen `KundeType` oder `null` zurückgibt.

`strawberry.ID` ist ein skalarer Typ in GraphQL, der serverseitig als String übermittelt
wird. Deshalb steht hier `int(kunde_id)` – die Konvertierung von String zu Integer
muss manuell erfolgen.

Wenn der Service `NotFoundError` wirft, gibt der Resolver `None` zurück statt die
Exception weiterzuleiten. GraphQL hat kein eingebautes HTTP-404-Konzept. Die Konvention
ist, `null` zurückzugeben, wenn ein angefragtes Objekt nicht existiert.

---

### 4.4 [`Query.kunden`](../../src/kunde/graphql_api/schema.py#L79)

#### Resolver für Filterabfragen

```python
@strawberry.field
def kunden(self, suchparameter: Suchparameter) -> Sequence[KundeType]:
    suchparameter_dict: Final[dict[str, str]] = dict(vars(suchparameter))
    suchparameter_filtered = {
        key: value
        for key, value in suchparameter_dict.items()
        if value is not None and value
    }
```

`vars(suchparameter)` wandelt das Strawberry-Eingabeobjekt in ein normales Python-Dictionary
um. Das ist nötig, weil der `KundeReadService` ein `Mapping[str, str]` erwartet und nichts
von Strawberry-Typen wissen soll.

Die Dict Comprehension danach filtert alle Felder heraus, deren Wert `None` oder ein leerer
String ist. Damit erreicht man, dass optionale Felder, die der Client nicht gesetzt hat,
die Suche nicht beeinflussen.

```python
    pageable: Final = Pageable.create(size=str(0))
    try:
        kunden_slice = _read_service.find(
            suchparameter=suchparameter_filtered, pageable=pageable
        )
    except NotFoundError:
        return []

    return [_to_kunde_type(dto) for dto in kunden_slice.content]
```

`size=str(0)` bedeutet: kein Limit, alle Treffer zurückgeben. Bei REST gibt es
Paginierung über Query-Parameter; bei dieser GraphQL-Implementierung wird darauf
verzichtet – der Client bekommt alle passenden Kunden auf einmal.

Beim `NotFoundError` wird eine leere Liste zurückgegeben. Das ist bei Listen die
saubere GraphQL-Konvention: Ein leeres Ergebnis ist kein Fehler, nur eine leere Menge.

---

### 4.5 [`Mutation.create`](../../src/kunde/graphql_api/schema.py#L113)

#### Resolver zum Anlegen eines neuen Kunden

```python
@strawberry.mutation
def create(self, kunde_input: KundeInput) -> CreatePayload:
    logger.debug("kunde_input={}", kunde_input)

    kunde_dict = kunde_input.__dict__
    kunde_dict["adresse"] = kunde_input.adresse.__dict__
```

`@strawberry.mutation` ist das Gegenstück zu `@strawberry.field`. Methoden mit
diesem Dekorator gehören zur GraphQL-Mutation, also zu schreibenden Operationen.

`kunde_input.__dict__` wandelt das Strawberry-Eingabeobjekt in ein Python-Dictionary um.
Dasselbe gilt für die verschachtelte Adresse: `kunde_input.adresse.__dict__` überführt
das `AdresseInput`-Objekt ebenfalls in ein normales Dictionary.

```python
    kunde_model: Final = KundeModel.model_validate(kunde_dict)
    kunde_dto: Final = _write_service.create(kunde=kunde_model.to_kunde())
    payload: Final = CreatePayload(id=kunde_dto.id)
    return payload
```

`KundeModel.model_validate(kunde_dict)` übergibt das Dictionary an Pydantic zur
Validierung. Damit wird dieselbe Validierungslogik genutzt wie beim REST-Endpunkt –
der Code wird nicht doppelt geschrieben. `to_kunde()` baut dann die eigentliche
`Kunde`-Entity, die der Write-Service in die Datenbank schreibt.

Am Ende wird aus der zurückgegebenen ID ein `CreatePayload` gebaut und zurückgegeben.

---

### 4.6 Schema und Router

#### [`Das fertige Schema`](../../src/kunde/graphql_api/schema.py#L134)

```python
schema: Final = strawberry.Schema(query=Query, mutation=Mutation)
```

`strawberry.Schema` ist der Einstiegspunkt: Es nimmt die beiden Resolver-Klassen
und baut daraus das vollständige GraphQL-Schema. Dieses Schema kennt alle Typen,
alle Felder und alle Resolver. Strawberry leitet eingehende GraphQL-Anfragen anhand
dieses Schemas an die richtigen Methoden weiter.

#### [`Kontext und Router`](../../src/kunde/graphql_api/schema.py#L137)

```python
Context = dict[str, Request]

def get_context(request: Request) -> Context:
    return {"request": request}

graphql_router: Final = GraphQLRouter[Context](
    schema, context_getter=get_context, graphql_ide=graphql_ide
)
```

`Context` ist ein Typ-Alias für das Dictionary, das Strawberry an jeden Resolver
weitergibt. Hier enthält es nur den FastAPI-`Request`, was ausreicht, um bei Bedarf
Header oder andere Request-Metadaten auszulesen.

`get_context` ist die Funktion, die Strawberry pro Request aufruft, um den Kontext
zu befüllen. Sie wird als `context_getter` an den `GraphQLRouter` übergeben.

`graphql_router` ist das Objekt, das in `fastapi_app.py` mit
`app.include_router(graphql_router, prefix="/graphql")` eingebunden wird.
`graphql_ide` steuert, ob GraphiQL – das Browser-basierte Testtool für GraphQL – aktiv
ist. Ob es aktiv ist, hängt von der Konfiguration in `config/graphql.py` ab.

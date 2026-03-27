# Beispiel mit FastAPI, VS Code und Docker

> Copyright 2023 - present [Jürgen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de), Hochschule Karlsruhe
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> at your option any later version
>
> This program is distributed in the hope that it will be useful
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details
>
> You should have received a copy of the GNU General Public License
> along with this program. If not, see <https://www.gnu.org/licenses/>
>
> Preview in VS Code durch `<Strg><Shift>v`

Durch das Kommando `Get-Command python` kann man in der PowerShell überprüfen,
ob man zum Aufsetzen der [virtuellen Umgebung](#virtuelle-umgebung)
die beabsichtigte .exe-Datei verwendet, und mit `python --version` überprüft man
die Version von Python.

Zunächst legt man ein Verzeichnis an, z.B. `C:\workspace\python\fastapi`.
In einer Shell (PowerShell bei Windows oder bash bei macOS) ruft man folgende
Kommandos auf:

```shell
    # uv aktualisiert sich ggf. selbst
    uv self update

    # Virtuelle Umgebung anlegen
    uv venv

    # Packages aus pyproject.toml installieren: dependencies und alle "dependency-groups"
    uv sync --all-groups
```

Bei VS Code wählt man durch die Funktionstaste _F1_ man in der _Kommandopalette_ den
Eintrag _Python: Interpreter auswählen_ mit dem Unterpunkt `.\.venv\Scripts\python.exe`
aus. Siehe https://code.visualstudio.com/docs/python/environments
Dadurch wird der Python-Interpreter der virtuellen Umgebung verwendet, die mit
_uv_ angelegt wurde.

## Inhalt

- [Beispiel mit FastAPI, VS Code und Docker](#beispiel-mit-fastapi-vs-code-und-docker)
  - [Inhalt](#inhalt)
  - [Allgemeine IT-Grundlagen](#allgemeine-it-grundlagen)
  - [Alternative Plattformen](#alternative-plattformen)
  - [Python Software Foundation](#python-software-foundation)
  - [PEP](#pep)
    - [PEPs ergänzend zur Programmiersprache](#peps-ergänzend-zur-programmiersprache)
    - [PEPs für Bestandteile der Programmiersprache und der Distribution](#peps-für-bestandteile-der-programmiersprache-und-der-distribution)
  - [Projektstruktur und Verzeichnisse](#projektstruktur-und-verzeichnisse)
    - ["src layout" statt "flat layout"](#src-layout-statt-flat-layout)
    - [Weitere Unterverzeichnisse](#weitere-unterverzeichnisse)
  - [Grundlagen Python](#grundlagen-python)
    - [Literatur](#literatur)
    - [Ausgewählte Datentypen aus der Python-Distribution](#ausgewählte-datentypen-aus-der-python-distribution)
    - [Blöcke zur Strukturierung](#blöcke-zur-strukturierung)
    - [Programmmier- und Namenskonventionen](#programmmier--und-namenskonventionen)
    - [truthy](#truthy)
    - [Package, Modul und import](#package-modul-und-import)
    - [Die Methoden \_\_init\_\_ und \_\_new\_\_](#die-methoden-__init__-und-__new__)
    - [public und private](#public-und-private)
    - [Module-level Singleton](#module-level-singleton)
    - [Decorators](#decorators)
    - [Logging](#logging)
  - [VS Code statt PyCharm als Entwicklungsumgebung](#vs-code-statt-pycharm-als-entwicklungsumgebung)
    - [VS Code](#vs-code)
    - [PyCharm](#pycharm)
    - [Entscheidung für VS Code](#entscheidung-für-vs-code)
  - [uv und pyproject.toml](#uv-und-pyprojecttoml)
    - [pip als Package Manager](#pip-als-package-manager)
    - [Alternative Package Manager](#alternative-package-manager)
    - [uv](#uv)
    - [Virtuelle Umgebung](#virtuelle-umgebung)
    - [pyproject.toml](#pyprojecttoml)(#installation-und-konfiguration-von-venv-und-pip-für-vs-code)
  - [uv und das Buildsystem](#uv-und-das-buildsystem)
    - [Wheel für Packages](#wheel-für-packages)
    - [Aufgaben eines Buildsystems](#aufgaben-eines-buildsystems)
    - [Buildsysteme](#buildsysteme)
    - [uv_build](#uv_build)
  - [Dokumentation](#dokumentation)
    - [reStructuredText (rST)](#restructuredtext-rst)
    - [Sphinx](#sphinx)
    - [MkDocs](#mkdocs)
    - [Generierung der Dokumentation mit MkDocs](#generierung-der-dokumentation-mit-mkdocs)
  - [Web-Frameworks, ASGI und WSGI](#web-frameworks-asgi-und-wsgi)
    - [WSGI](#wsgi)
    - [ASGI](#asgi)
    - [Web- und REST-Frameworks](#web--und-rest-frameworks)
  - [OR-Mapping](#or-mapping)
  - [Validierung](#validierung)
  - [GraphQL](#graphql)
  - [DB-Server und DB-Browser](#db-server-und-db-browser)
  - [Applikationsserver](#applikationsserver)
    - [localhost, 127.0.0.1 und 0.0.0.0](#localhost-127001-und-0000)
    - [HTTPS](#https)
    - [Serverstart](#serverstart)
  - [Docker Images, Container und Docker Compose](#docker-images-container-und-docker-compose)
    - [Minimales Basis-Image](#minimales-basis-image)
    - [Image erstellen](#image-erstellen)
    - [Image inspizieren](#image-inspizieren)
      - [docker history](#docker-history)
      - [docker inspect](#docker-inspect)
      - [docker sbom](#docker-sbom)
    - [Docker Compose](#docker-compose)
  - [Statische Codeanalyse](#statische-codeanalyse)
    - [Statische Codeanalyse im Überblick](#statische-codeanalyse-im-überblick)
    - [ruff](#ruff)
    - [SonarQube](#sonarqube)
  - [Code Formatter](#code-formatter)
    - [ruff statt Black](#ruff-statt-black)
    - [black](#black)
    - [autopep8](#autopep8)
    - [YAPF](#yapf)
    - [isort](#isort)
  - [Analyse für Sicherheitslücken](#analyse-für-sicherheitslücken)
    - [OWASP Dependency Check](#owasp-dependency-check)
    - [ruff statt Bandit](#ruff-statt-bandit)
    - [Docker Scout](#docker-scout)
  - [Testen](#testen)
    - [pytest statt unittest](#pytest-statt-unittest)
    - [HTTP-Client für Integrationstests](#http-client-für-integrationstests)
    - [Backend-Server und Appserver als Voraussetzung für Integrationstests](#backend-server-und-appserver-als-voraussetzung-für-integrationstests)
    - [pytest in der Kommandozeile](#pytest-in-der-kommandozeile)
    - [pytest mit VS Code](#pytest-mit-vs-code)
    - [locust für Lasttests](#locust-für-lasttests)
- [Port bereits belegt?](#port-bereits-belegt)

## Allgemeine IT-Grundlagen

- Agile Softwareentwicklung, z.B. SCRUM, und Unified Process
- Architektur
- Schichtenarchitektur, z.B.
  - Präsentationsschicht
  - Geschäftslogik
  - Datenbankzugriffsschicht (besser: Integrationsschicht)
- Schnittstellen mit REST, GraphQL, evtl. gRPC
- Design Patterns, vor allem Singleton, Factory, Fassade, Observer, Proxy
- UML, vor allem
  - Use-Case-Diagramm
  - Komponentendiagramm
  - Klassendiagramm
  - Zustandsdiagramm für GUIs
- Objektorientierte und funktionale Programmierung mit Java, JavaScript/TypeScript, Python
- Dependency Injection
- Relationale DB-Systeme und SQL einschließlich
  - Schema wie in z.B. Oracle und PostgreSQL
  - CREATE TABLE mit Spaltentypen und Constraints
  - Normalisierung, z.B. 3NF
  - Indexe durch B+ Bäume
  - ACID-Transaktionen: Atomicity, Consistency, Isolation, Durability
  - Isolationslevel: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE
  - Konsistenzbegriffe, z.B. MVCC
  - https://architecturenotes.co/things-you-should-know-about-databases
- ER-Diagramme einschließlich Krähenfußnotation
- Docker und Kubernetes
- Konfigurationsdateien
  - .toml
  - .json
  - .ini
  - .env
- Öffentliche und private Schlüssel durch z.B. RSA
- Wireframes für grafische Prototypen
- Web-Technologien: React, Angular, ..., MUI, Bootstrap, Material Icons, Font Awesome, Sass/CSS,
- Apps mit Android und iOS

## Alternative Plattformen

Funktionalität | Java | JavaScript, TypeScript
:------------- | :--- | :---------------------
Laufzeitumgebung mit HTTP-Schnittstelle | Tomcat von Apache <br /> Jetty von Eclipse <br /> Undertow von Red Hat | Node <br /> Deno <br /> Bun
REST | Spring Web MVC <br /> Jakarta RESTful Web Services | Express <br /> Nest
Events, z.B. Startup | Interface "CommandLineRunner" bei Spring | Interface "OnApplicationBootstrap" bei Nest <br /> "app.on()" bei Express
Filter für Requests, z.B. für Security | @RolesAllowed bei Spring Security <br /> Interface "Filter" bei Spring | Decorators oder Interface "NestMiddleware" bei Nest <br /> Middleware mit "app.use()" oder "router.use()" bei Express
GraphQL | Spring for GraphQL <br /> Microprofile GraphQL von Eclipse | Apollo GraphQL
OpenAPI | springdoc-openapi | @nestjs/swagger
OR-Mapping | Spring Data JPA <br /> Hibernate / Jakarta Persistence  <br /> Jakarta Data | TypeORM <br /> Prisma
Validierung | Hibernate Validator | class-validator <br /> Ajv
HTTP-Client | HTTP-Interface von Spring 6 <br /> OkHttp | Axios <br /> got <br /> Fetch API
JWT = JSON Web Token | Spring Security | Passport
Passwortverschlüsselung: Argon2, bcrypt | Spring Security | argon2 <br /> bcrypt
XSS, CSRF, HSTS, CSP, X-Frame-Options | Spring Security | Helmet
Testen | JUnit | Vitest (Jest) <br /> Playwright (Cypress)
Codeanalyse | Errorprone <br /> CheckStyle <br /> SpotBugs <br /> PMD <br /> SonarQube | ESLint <br /> SonarQube
Code-Formatierung | Spotless | Prettier
Buildsystem | Maven <br /> Gradle | npm-Skripte <br /> Gulp
Dokumentation | AsciiDoctor <br /> Javadoc <br /> PlantUML | AsciiDoctor <br /> JSDoc <br /> TypeDoc <br /> PlantUML

## Python Software Foundation

Die Python Software Foundation https://www.python.org/psf-landing

- stellt die Infrastruktur bereit für https://python.org
- stellt die Infrastruktur bereit für _The Python Package Index_ https://pypi.org
- hat 1994 den 1. Python Workshop durchgeführt https://legacy.python.org/workshops
- organisiert seit 2008 die Konferenz _PyCon US_

## PEP

_PEP_ steht für "Python Enhancement Proposal" und ist vergleichbar mit _JEP_
= JDK Enhancement-Proposal für Java https://openjdk.org/jeps oder den
_ECMAScript Proposals_ für JavaScript.

Guido van Rossum (*1956) hatte von 1989 bis 2018 den ironischen Ehrentitel
_Benevolent dictator for life_ (BDFL) und hat in dieser Rolle die PEPs
abgezeichnet. Seit 2018 gibt es ein _Steering Council_ (s.u.) bestehend aus
5 Personen.

### PEPs ergänzend zur Programmiersprache

PEP | Jahr | URL
:-- | :--- | :--
The Zen of Python | 2004 | https://github.com/python/peps/blob/main/peps/pep-0020.rst
Releaseplan für Python für 3.14 | 2024 | https://github.com/python/peps/blob/main/peps/pep-0745.rst
Releaseplan für Python für 3.13 | 2023 | https://github.com/python/peps/blob/main/peps/pep-0719.rst
Python Database API Specification v2.0 | 1999 | https://github.com/python/peps/blob/main/peps/pep-0249.rst
Style Guide | 2001 | https://peps.python.org/pep-0008
docstrings | 2001 | https://peps.python.org/pep-0257
Web Server Gateway Interface (WSGI) v1.0.1 | 2010 | https://peps.python.org/pep-3333
Version Identification and Dependency Specification | 2013 | https://peps.python.org/pep-0440
A build-system independent format for source trees | 2015 | https://peps.python.org/pep-0517
Specifying Minimum Build System Requirements for Python Projects | 2016 | https://peps.python.org/pep-0518
Python Language Governance | 2018 | https://peps.python.org/pep-0013
Annual Release Cycle for Python | 2019 | https://github.com/python/peps/blob/main/peps/pep-0602.rst
Storing project metadata in `pyproject.toml` | 2020 | https://github.com/python/peps/blob/main/peps/pep-0621.rst <br /> https://packaging.python.org/en/latest/specifications
Require virtual environments by default for package installers | 2023 | https://github.com/python/peps/blob/main/peps/pep-0704.rst
Adding iOS as a supported platform | 2023 | https://github.com/python/peps/blob/main/peps/pep-0730.rst
Adding Android as a supported platform | 2023 | https://github.com/python/peps/blob/main/peps/pep-0738.rst
A file format to record Python dependencies for installation reproducibility | 2025 | https://github.com/python/peps/blob/main/peps/pep-0751.rst

Beachte: zu [ASGI = Asynchronous Server Gateway Interface](#asgi) gibt es kein PEP
https://asgi.readthedocs.io.

_Python Readiness_:

- https://pyreadiness.org/3.11
- https://pyreadiness.org/3.12

_The Zen of Python_:

> Beautiful is better than ugly. <br />
> Explicit is better than implicit. <br />
> Simple is better than complex. <br />
> Complex is better than complicated. <br />
> Flat is better than nested. <br />
> Sparse is better than dense. (sparse = spärlich, karg; dense = dicht) <br />
> Readability counts. <br />
> Special cases aren't special enough to break the rules. <br />
> Although practicality beats purity. <br />
> Errors should never pass silently. <br />
> Unless explicitly silenced.
> In the face of ambiguity, refuse the temptation to guess. <br />
> There should be one -- and preferably only one -- obvious way to do it. <br />
> Although that way may not be obvious at first unless you're Dutch. <br />
> Now is better than never. <br />
> Although never is often better than _right_ now. <br />
> If the implementation is hard to explain, it's a bad idea. <br />
> If the implementation is easy to explain, it may be a good idea. <br />
> Namespaces are one honking great idea -- let's do more of those! (to honk = hupen) <br />

### PEPs für Bestandteile der Programmiersprache und der Distribution

PEP | Python | Jahr | URL
:-- | :----- | :--- | :--
_venv_ als virtuelle Umgebung | 3.3 | 2011 | https://peps.python.org/pep-0405 <br /> https://github.com/python/peps/blob/main/peps/pep-0405.txt
_pip_ als Package Manager | 3.4 | 2013 | https://peps.python.org/pep-0453
<s>Python Local Package Directory</s> | 3.12 | 2023 | https://peps.python.org/pep-0582
List Comprehension | 2.0 | 2000 | https://peps.python.org/pep-0202
Logging System | 2.3 | 2002 | https://peps.python.org/pep-0282
Decorators for Functions and Methods | 2.4 | 2004 | https://peps.python.org/pep-0318
Imports: Multi-Line and Absolute/Relative | 2.5 | 2006 | https://peps.python.org/pep-0328
Conditional Expressions | 2.5 | | https://peps.python.org/pep-0308
The `with` Statement | 2.5 | | https://peps.python.org/pep-0343
Class Decorators | 3.0 | 2008 | https://peps.python.org/pep-3129
Dict Comprehension | 3.0 | | https://peps.python.org/pep-0274
`Enum` | 3.4 | 2013 | https://peps.python.org/pep-0435
`pathlib` Modul | 3.4 | | https://peps.python.org/pep-0428
Type Hints | 3.5 | 2015 | https://peps.python.org/pep-0483
`typing` Modul | 3.5 | | https://peps.python.org/pep-0484
`async`, `await`, `Coroutine` | 3.5 | | https://peps.python.org/pep-0492
Type Hints für Variable | 3.6 | 2016 | https://peps.python.org/pep-0526
`f`-Strings | 3.6 <br /> 3.12 | <br /> 2023 | https://peps.python.org/pep-0498 <br /> https://github.com/python/peps/blob/main/peps/pep-0701.rst
`@dataclass` | 3.7 | 2018 | https://github.com/python/peps/blob/main/peps/pep-0557.rst
`Final` | 3.8 | 2019 | https://github.com/python/peps/blob/main/peps/pep-0591.rst
Assignment Expressions (_walrus operator_) | 3.8 | | https://github.com/python/peps/blob/main/peps/pep-0572.rst
Union Operator \| | 3.10 | 2021 | https://github.com/python/peps/blob/main/peps/pep-0604.rst
Structural Pattern Matching | 3.10 | | https://github.com/python/peps/blob/main/peps/pep-0634.rst
`Self` | 3.11 | 2022 | https://github.com/python/peps/blob/main/peps/pep-0673.rst
`tomllib`: Support for Parsing TOML in the Standard Library | 3.11 | | https://github.com/python/peps/blob/main/peps/pep-0680.rst
Type Parameter Syntax | 3.12 | 2023 | https://github.com/python/peps/blob/main/peps/pep-0695.rst
Inlined comprehensions | 3.12 | | https://github.com/python/peps/blob/main/peps/pep-0709.rst
frozendict | 3.15 | 2026? | https://github.com/python/peps/blob/main/peps/pep-0814.rst

## Projektstruktur und Verzeichnisse

### "src layout" statt "flat layout"

Der eigentliche Python-Code für die Auslieferung wird vom Code für die Tests
getrennt, indem die beiden Unterverzeichnisse `src` und `tests` verwendet werden,
wie es in den meisten Python-Projekten seit ca. 2015 üblich ist. Unterhalb
von src gibt es ein weiteres Unterverzeichnis mit dem _Namen des eigenen
Python-Packages_ (hier: kunde).

Wenn man mit [uv](#uv) als "Package und Projectmanager" durch `uv init` ein neues Projekt
anlegt, erhält man das "src layout". Ebenso wenn man Hatch als [Buildsystem](#buildsysteme)
verwendet und ein Projekt mit `hatch new` aufsetzt.

- https://packaging.python.org/en/latest/tutorials/packaging-projects
- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout
- https://py-pkgs.org/04-package-structure.html#the-source-layout
- https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
- https://bskinn.github.io/My-How-Why-Pyproject-Src
- https://hynek.me/articles/testing-packaging
- https://snarky.ca/clarifying-pep-518

### Weitere Unterverzeichnisse

- `extras`
  - `postgres`: SQL-Skripte und CSV-Dateien für _PostgreSQL_
  - `compose`: Dateien für Docker Compose
  - `bruno`: .bru-Dateien für Collection in _Bruno_
- `.venv`: Virtuelle Umgebung mit _venv_
- `.vscode`: Konfigurationsdatei `settings.json` für _VS Code_
- `docs`: Generierung der API-Dokumentation mit _mkdocs_

## Grundlagen Python

### Literatur

- Allen B. Downey:
  "Think Python 2e".
  O'Reilly Media, 2. Edition, 2016.
  https://greenteapress.com/wp/think-python-2e
- https://docs.python.org/3/tutorial
- https://www.iwi-hka.de/vorkurs
- https://drive.google.com/drive/folders/1Dl5Z7Yjv1FQNesqjIy7e6BeeQY6FNwfo

### Ausgewählte Datentypen aus der Python-Distribution

- str
- int
- float
- Decimal
- bool
- None
- list
- set
- dict
- tuple
- Sequence
- Enum
- IntEnum
- StrEnum
- Literal
- Self
- Generics durch [ ]
- | für Union
- date
- datetime
- HTTPStatus
- Path
- Logger
- Any

### Blöcke zur Strukturierung

- durch Einrücken
- `:` am Zeilenende bei `def` (Funktionen), `if`, `match`, `for .. in`, `while`
- statt `{ ... }`

### Programmmier- und Namenskonventionen

- "Style Guide for Python Code" PEP 8 von 2001, https://peps.python.org/pep-0008
- Klassen mit CamelCase
- Funktionen und Variable mit snake_case
- Konstante mit UPPERCASE bzw. SCREAMING_SNAKE_CASE
- public
  - selbsterklärend
  - wird in Zukunft nicht geändert
  - dokumentiert
- _non-public_: private gibt es nicht
  - `_` als Präfix
  - `__` als Präfix mit _name mangling_: __my_method wird zu_MyClass__my_method <br/>
    Ziel: keine Verwendung bei Vererbung
  - _dunder_, z.B. `__init__`
- absolute Imports
- _keyword arguments_ bei Funktionsaufrufen; vgl.:
  - Destructuring beim Funktionsaufruf in JavaScript und TypeScript
  - named arguments bei Kotlin
- Decorator `@dataclass` für Entity-Klassen, ab Python 3.7 (2018),
  https://peps.python.org/pep-0557; vgl.:
  - `record` in Java
  - `interface` bei TypeScript
  - `data class` in Kotlin
- Funktionen und globale Variable für den Export in `__all__` deklarieren
- "Throw Exceptions Instead of Returning Errors"
- Suffix `Error` für Exceptions
- Zeilenlänge `88`
  - Kommentare für _Type Checker_, z.B. `# pylint: disable=not-callable`
  - Defaultwert bei _Black_ zur Code-Formatierung https://black.readthedocs.io.
    vgl.: _Prettier_ in JavaScript
- Strings durch double-quotes
  - Defaultwert bei _Black_ zur Code-Formatierung
  - Anwendung bei [docstrings](#restructuredtext-rst)
- _Type Hints_ für _Type Checker_
- _List Comprehension_: "is also a good practice to write code in a pythonic way"
  https://levelup.gitconnected.com/7-bad-habits-that-every-python-programmer-should-avoid-d477ea91e7da
- `with`-Block.
  vgl.: `Autoclosable` in Java, z.B. bei "try with resources"
- _docstrings_ mit `"""` seit 2001, https://peps.python.org/pep-0257; vgl.:
  - _javadoc_ für Java
  - _JSdoc_ für JavaScript
  - _TypeDoc_ für TypeScript
  - _KDoc_ für Kotlin

### truthy

- Zahlen: 0 = False, sonst True
- list, tuple, str, dict, set: leer = False, sonst True
- None = False

### Package, Modul und import

Ein Python-Package enthält mindestens ein Modul, d.h. es gibt `src/<package_name>`
mit mindestens einem Unterverzeichnis, das eine Datei `__init__.py` enthält, z.B.
`src\kunde\router`. _import_ eines Moduls entspricht quasi dem Importieren der Datei
`__init__.py` und all dessen, was dort in `__all__` aufgelistet ist.

### Die Methoden \_\_init\_\_ und \_\_new\_\_

`__init__` entspricht dem Konstruktor in objektorientieren Programmiersprachen,
wie z.B. Java. \_\_init\_\_ wird aufgerufen, wenn ein Objekt instanziiert wird,
um ein "Customizing" des neues Objekts vorzunehmen, nachdem mit der statischen
Methode `__new__` das neue Objekt erzeugt wurde. Details siehe
https://docs.python.org/3/reference/datamodel.html#object.\_\_init\_\_und
https://docs.python.org/3/reference/datamodel.html#object.\_\_new\_\_

### public und private

Alles in einer Klasse ist public: Python ist nicht so restriktiv wie typische
objektorientierte Sprachen. Frei nach Guido van Rossum: _"consenting adult
principle: users of your code will use it responsibly"_.

Private realisiert man durch 2 führende Unterstriche, z.B. `__nachname`.
Tatsächlich handelt es sich aber um _Name Mangling_, d.h. man kann trotzdem von
außen zugreifen, z.B. `my_object.__MyClass_nachname`. Siehe
https://docs.python.org/3/tutorial/classes.html#private-variables.

### Module-level Singleton

Module sind per Definition Singletons: _Funktionen_ kann man in anderen Moduln
importieren und aufrufen. _Variable_ speichern die Daten bzw. den Zustand,
falls es einen gibt. Das ist ein typischer Python-Programmierstil (**pythonic**).

### Decorators

Durch das _Decorator Pattern_ werden Objekte um zusätzliche Funktionalität ergänzt
("dekoriert"), ohne ihre interne Struktur zu ändern. Das Decorator Pattern wird
typischerweise angewendet auf:

- Klassen als "first-class objects"
- Funktionen als "first-class objects" einschl. der Rückgabewerte
- Argumente der Funktionen

Beispiel mit Python:

```python
def my_decorator(decorated_func):
    def decorator_impl(*args, **kwargs):
        print("Implementierung des Decorators durch decorator_impl")
        return decorated_func(*args, **kwargs)
    return decorator_impl

@my_decorator
def example_func():
    print("example_func wird aufgerufen")

example_func()
```

### Logging

Logging erfolgt durch _loguru_ statt logging aus der Python-Standardbibliothek:

- 23.400 Stars bei GitHub
- in 137.000 Repositories bei GitHub genutzt
- 70 Contributors
- https://loguru.readthedocs.io
- https://github.com/Delgan/loguru

## VS Code statt PyCharm als Entwicklungsumgebung

### VS Code

_VS Code_ ist von Microsoft. Dort arbeitet _Guido von Rossum_ der Erfinder von
Python (1989) seit 2020 als _Distinguished Engineer_ in der _Developer Division_.
Zuvor war er viele Jahre u.a. bei Google und Dropbox. Bei Verwendung von VS Code
empfiehlt es sich, monatlich die Blogeinträge bei https://devblogs.microsoft.com/python
zu lesen.

Empfohlene Erweiterungen, die fast alle von Microsoft entwickelt werden:

- _Python_
  - 150+ Mio Mal heruntergeladen
  - Code Navigation
  - Refactoring
  - Formatierung
  - installiert Pylance (s.u.) und _isort_ implizit mit
  - Unterstützung für _venv_
  - Syntaxunterstützung für `pyproject.toml`
- _Pylance_ als "Type Checking Tool" auf Basis von _Pyright_
- _isort_, herausgelöst aus der Erweiterung _Pylance_
- _pylint_, herausgelöst aus der Erweiterung _Pylance_
- _flake8_, herausgelöst aus der Erweiterung _Pylance_
- _Black Formatter_, herausgelöst aus der Erweiterung _Pylance_

Um _Pyright_ auch von der Kommandozeile nutzen zu können, installiert man es
durch `npm i -g pyright`, weil es in TypeScript für die Erweiterung _Pylance_
zu VS Code entwickelt ist.

Die Einstellungen für VS Code kann man global über das Settings-Icon in der
Werkzeugleiste vornehmen, was dann in `$env:APPDATA\Code\User\settings.json`
gespeichert wird. Die globalen Einstellungen kann man projektspezifisch in
`.vscode\settings.json` überschreiben. Details siehe
https://code.visualstudio.com/docs/python/settings-reference.

### PyCharm

_PyCharm_ von JetBrains unterstützt durch _Wizards_ das Erstellen eines neuen Projekts.
Es gibt Wizards u.a. für _Django_, _FastAPI_ und  _Flask, wobei auch ein
"Virtual Environment" mit _venv_ eingerichtet wird - allerdings nicht die aktuelle
Version.

Während die Erweiterungen für VS Code ständig und vor allem durch Microsoft
aktualisiert werden, gibt es für PyCharm nur die Plugins _Mypy_ und _Pylint_.
Diese werden auch nur von Einzelpersonen entwickelt und wurden seit über 1 Jahr
nicht aktualisiert.

### Entscheidung für VS Code

- Der Hersteller _Microsoft_ ist im ganzen Python-Umfeld ein "ganz starker Player",
  während JetBrains ein etablierter Hersteller von IDEs ist.
- _Guido van Rossum_, der Erfinder von Python, ist als _Distinguished Engineer_ in
  der Developer Division von Microsoft
- _Erweiterung Python_ wurde über 150 Mio. Mal heruntergeladen
- Weitere Erweiterungen von Microsoft selbst: Pylance einschl. pyright, isort,
  pylint und Black Formatter
- In den Artikeln zu Python in der "Fundgrube" https://medium.com wird durchweg
  VS Code verwendet
- Twitter-Account _@pythonvscode_
- Umfangreiches Angebot für Data Science bzw. Machine Learning in der _Azure Cloud_

**ERNSTER HINWEIS**: Wenn Data Science in der Cloud eines IT-Konzerns wie Amazon,
Microsoft oder Google genutzt werden soll, so benötigt man dafür ein entsprechendes
Datenvolumen, d.h. alle unsere Daten laden wir in die Cloud eines außer-europäischen
IT-Konzerns. Was bedeutet das für die Zukunft Europas? Technologisch? Wirtschaftlich?

## uv und pyproject.toml

### pip als Package Manager

- _pip_ = "Pip Installs Packages", d.h. _external packages_ installieren, wie z.B.
  Django, FastAPI, Flask, SQLAlchemy uvm.
- Bestandteil der Python-Distribution seit Python 3.4 (2013)
- PEP 453 https://peps.python.org/pep-0453
- Entwickelt von _PyPA_ = Python Packaging Authority
- _PyPI_ = Python Package Index https://pypi.org, vgl.:
  - Maven-Repositories für Java https://repo.maven.apache.org/maven2
  - NPM-Packages für JavaScript https://www.npmjs.com
- Konfigurationsdatei, z.B. für eine virtuelle Umgebung:
  - `requirements.txt` https://pip.pypa.io/en/stable/reference/requirements-file-format
  - `pyproject.toml` siehe https://packaging.python.org/en/latest/specifications/declaring-project-metadata
    und PyPA specifications https://packaging.python.org/en/latest/specifications
    ursprüngl. https://peps.python.org/pep-0621; vgl.:
    - pom.xml für Maven
    - build.gradle.kts für Gradle
    - package.json für JavaScript

Beim Installieren mit _pip_ werden die zu installierenden Packages von
https://pypi.org heruntergeladen und in einem Cache gepuffert
https://pip.pypa.io/en/stable/topics/caching:

Betriebssystem | Verzeichnis
:------------- | :----------------------------
Windows        | `$env:LOCALAPPDATA\pip\Cache`
Linux          | `~/.cache/pip`
MacOS          | `~/Library/Caches/pip`

### Alternative Package Manager

- _Conda_ (Package Manager + Buildsystem + Virtuelle Umgebung)
  - für _Anaconda Python_
  - Projekte für Data Science
  - unterstützt virtuelle Umgebungen
  - Buildsystem für eigene Packages
  - auch von VS Code unterstützt
  - Upload von Packages zu https://anaconda.org
- _Poetry_
  - hat `pyproject.toml` populär gemacht
  - befolgt nicht exakt https://peps.python.org/pep-0621, da es älter ist
  - unterstützt virtuelle Umgebungen
  - beinhaltet ein Buildsystem (statt z.B. uv_build oder Hatch), um ein Wheel zu bauen
  - Publishing zu https://pypi.org
- _pipenv_: Integration von pip und virtualenv (s.u.)
- _uv_

### uv

- extrem schnell: implementiert in Rust
- Package und "Project Manager" einschließlich virtueller Umgebung
- vom Unternehmen _Astral_ ("Next-Gen Python Tooling"): https://astral.sh
- Unter Mitwirkung von Charlie Marsh (Initiator von _ruff_ zur schnellen Codeanalyse)
- 40.000+ Stars bei GitHub
- https://github.com/astral-sh/uv
- https://astral.sh/blog/uv

In einer Shell (PowerShell bei Windows oder bash bei macOS) kann man folgende
Kommandos aufrufen:

```shell
    # uv aktualisiert sich ggf. selbst
    uv self update

    # Packages aus pyproject.toml installieren: dependencies und alle "dependency-groups"
    uv sync --all-groups
```

### Virtuelle Umgebung

Ohne eine virtuelle Umgebung installiert pip alle _external packages_
("third-party libraries")

- bei Windows: in der Python-Installation im Verzeichnis `site-packages`
- bei Linux in `/usr/local`.

Und zwar für **alle** Projekte. Das führt zur sogenannten _System Pollution_ sowie
zu Versionskonflikten, wenn verschiedene Projekte verschiedene Versionen benötigen.

Eine virtuelle Umgebung ist eine isolierte Umgebung für die Verzeichnissstruktur
eines Projekts (vgl. `node_modules` bei JavaScript):

- eine bestimmte Python-Version sowie
- die benötigten und passenden Python-Packages, z.B. _Django_, _FastAPI_, _Flask_,
  _SQLAlchemy_

_venv_ ist als virtuelle Umgebung weit verbreitet:

- `.venv\Scripts` wird PATH vorangestellt, z.B. für `python`, `pip`, `mypy` und
  `pytest`
- `.venv\Lib\site-packages` für die benötigten Python-Packages, z.B. _Django_,
 _FastAPI_,  _Flask_, _SQLAlchemy_
- Bestandteil der Python-Distribution seit Python 3.3 (2011)
- genutzt von _uv_
- https://docs.python.org/3/library/venv.html
- PEP 405 https://peps.python.org/pep-0405
- Hervorgegangen aus _virtualenv_ http://www.virtualenv.org

Alternativen zu venv sind:

- _Conda_ (siehe: "Alternative Package Manager")
- _Poetry_
- _virtualenv_: Obermenge von venv, kann auch mit Python 2 genutzt werden
- _pipenv_: Integration von pip und virtualenv

### pyproject.toml

Bei Java bezeichnet man _Maven_ und _Gradle_ als Buildsysteme, d.h. sie verwalten
die Abhängigkeiten ("Dependencies") von externer Software _UND_ können Aufgaben
für das Bauen der Software erledigen, wie z.B. Übersetzen, Tests aufrufen,
statische Codeanalyse durchführen, Dokumentation generieren uvm. Auch bei JavaScript
bzw. Node gibt es in _package.json_ diese beiden Aufgabenbereiche: (dev)dependencies
und die Deklaration der scripts.

Mit der Datei `requirements.txt` gemäß https://pip.pypa.io/en/stable/reference/requirements-file-format
kann man jedoch nur die Abhängigkeiten von "external Packages" spezifizieren.
Dabei kann man jedoch nicht differenzieren, ob ein external Package für die
Auslieferung oder für die Tests oder für die Codeanalyse oder für die Dokumentation
ist, so dass man mehrere requirements-Dateien benötigt, die man bei der Installation
entsprechend referenzieren kann.

Außerdem ist mit requirements.txt die Konfiguration der vielfältigen Werkzeuge
nicht möglich und man hat deshalb eine Vielzahl zusätzlicher Konfigurationsdateien,
wie z.B. `pyrightconfig.json`, `pytest.ini`, `setup.cfg` oder `config.toml`.

Mit `Pipfile` https://github.com/pypa/pipfile gibt es zwar inzwischen die
Möglichkeit, eine Datei im Format TOML für die diversen Dependency-Varianten zu
erstellen, doch das Problem der Werkzeug-Konfigurationen bleibt bestehen.
Außerdem steht bei https://github.com/pypa/pipfile "This format is still under
active design and development", während gleichzeitig das letze Commit im März
2022 war.

Durch `pyproject.toml` mit dem PEP https://peps.python.org/pep-0621 von 2020
hat man nun aber die Möglichkeit, sowohl die Dependencies für _pip_ als auch
die Konfiguration der Werkzeuge zentralisiert vorzunehmen:

- Metadaten zum Projekt:
  - Name
  - Versionsnummer
  - Minimalanforderung an die Python-Version
  - ReadMe-Datei
  - Lizenz-Datei
  - Autoren
  - Entwicklungszustand: Alpha, Beta, Release Candidate, Stable
- Dependencies
- Optionale Dependencies, z.B.
  - test
  - quality
  - doc
  - util
- Projekt-URLs
  - Homepage
  - Dokumentation
  - (Git-) Repository
  - Changelog
- Konfiguration der Werkzeuge, z.B.
  - pytest
  - uv
  - uv_build

## uv und das Buildsystem

### Wheel für Packages

- _distutils_ ist das Original "Packaging System", um eine Python-Distribution zu bauen;
  ab Python 3.12 ist distutils nicht mehr in der Python-Distribution enthalten.
- _setuptools_ sind eine Erweiterung zu den _distutils_, um Packages im Format
  _Egg_ zu erstellen; auch setuptools ist ab Python 3.12 nicht mehr in der
  Python-Distribution enthalten.
- _Wheel_ löst das Format _Egg_ ab.

Wheel als "Binary Distribution Format" für die Installation durch uv, pip usw.:

- Ein Wheel ist ein ZIP-Archiv mit der Endung `.whl`, z.B.
  - `{distribution}-{version}-{python tag}-{abi tag}-{platform tag}.whl`
  - distribution: `django`, `fastapi`, ...
  - version: `4.1.6`, `2026.4.1`, ...
  - python tag: z.B. `py3`
  - abi tag (Application Binary Interface): z.B. `none` oder `abi3`.
    Binäre Repräsentation der Datenstrukturen und Funktionen, um Kompatibilität
    zwischen CPython, PyPy https://www.pypy.org und Jython https://www.jython.org
    (Python-Implementierung für die JVM) zu gewährleisten.
  - platform tag: z.B. `any`, `win_amd64`, `macosx_13_0_x86_64`, `linux_x86_64`.
  - _Platform Compatibility Tags_: {python tag}-{abi tag}-{platform tag}
    https://packaging.python.org/en/latest/specifications/platform-compatibility-tags
- Wheels werden beim Installieren i.a. heruntergeladen von:
  - https://pypi.org (PyPI = Python Package Index) oder
  - Git-Repository, z.B. bei GitHub oder GitLab
- Datei `WHEEL` im Unterverzeichnis `<PACKAGE>-<VERSION>.dist-info` enthält die
  Metadaten über das ZIP-Archiv; vgl. `Manifest.mf` bei JAR-Dateien für die Java-Plattform
- _wheel_ wird unterstützt durch den Package Manager [pip](#pip-als-package-manager)
- https://packaging.python.org/en/latest/specifications/binary-distribution-format
- ursprünglich https://peps.python.org/pep-0427

### Aufgaben eines Buildsystems

- Wheel einschließlich der abhängigen Dependencies erstellen
- ggf. Source-Distribution erstellen
- "Publishing" bzw. Hochladen des Wheels nach https://pypi.org

### Buildsysteme

- Hatch
  - Referenz bei https://packaging.python.org/en/latest/tutorials/packaging-projects
  - Default-Buildsystem, wenn man mit `uv init` ein neues Projekt erstellt
  - Konfiguration bei Windows in ${env:LOCALAPPDATA}\hatch\config.toml
  - seit 2017
  - https://hatch.pypa.io
  - https://github.com/pypa/hatch
- Flit
  - leichtgewichtiger als Hatch, z.B. Test können nicht gestartet werden, Dokumentation
    kann nicht gebaut werden
  - seit 2018
  - https://flit.pypa.io
  - https://github.com/pypa/flit
- Conda (Package Manager + Buildsystem + Virtuelle Umgebung)
- Poetry (Package Manager + Buildsystem + Virtuelle Umgebung)
- uv_build (s.u.)

Buildsystem   | Genutzt von
:------------ | :----------
_Hatch_       | Hatch

              | FastAPI
              | Starlette
              | Pydantic
              | uvicorn
              | httpx
              | MkDocs
_Flit_        | Flit
              | Wheel
              | Flask
_Poetry_      | Poetry
              | Strawberry GraphQL
_setuptools_  | setuptools
              | SQLAlchemy
              | pyOpenSSL
              | cryptography
              | pytest
              | locust
              | Loguru

### uv_build

`uv build` erstellt im Verzeichnis `dist` ein Wheel für _PyPI_ (Python Package Index)
und  eine "Source-Distribution" z.B. `kunde-<VERSION>.tar.gz`.

Das Wheel `kunde-<VERSION>-py3-none-any.whl` wird dabei gemäß
https://packaging.python.org/en/latest/specifications/binary-distribution-format
erstellt. Die einzelnen Teile des Dateinamens bedeuten:

- Package-Name (hier: kunde)
- Versionsnummer
- `py3`: das Package ist für Python 3 und nicht auch für Python 2
- `none`: es wird kein bestimmtes ABI ("application binary interface") vorausgesetzt für
  die Kompatibilität zwischen CPython, PyPI und Jython (d.h. Python auf Basis von JVM)
- `any`: es wird keine bestimmte Plattform vorausgesetzt statt `win_amd64`,
  `macosx_13_0_x86_64`, `linux_x86_64`.

Mit `uv publish --token <PYPI_TOKEN>` kann dann das Wheel für PyPI hochgeladen werden.

_uv_build_ ist in der Distribution für uv enthalten ("bundled"). Wenn man ein neues
Projekt mit `uv init` aufsetzt, ist uv_build der Defaultwert für das Buildsystem siehe:

- https://docs.astral.sh/uv/concepts/build-backend
- https://docs.astral.sh/uv/guides/package

## Dokumentation

### reStructuredText (rST)

- Dateiendung `.rst`
- _Markup-Sprache_ wie HTML oder Markdown
- mehr Features als Markdown
- verwendet in _docstrings_ zur API-Dokumentation in Python

Beispiel für docstrings:

```rst
    :param arg1: Beschreibung des Arguments arg1
    :return: Beschreibung der Rückgabewertes
    :rtype: Rückgabetyp
    :raises MyError: Beschreibung der Exception
```

Ausgewählte Syntax:

- `*text*`: kursiv
- `**text**`: fett
- ` ``text`` `: monospaced, d.h. durch 2x Backticks bzw. Backquotes
- `*`: nicht-nummerierte Liste
- `#`: nummerierte Liste
- _Schachtelung von Listen_ durch Einrücken
- _(Unter-) Kapitel_ https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections
- _Inhaltsverzeichnis_ ("Table of Contents", "ToC")
- _Tabellen_ https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#tables

Literatur:

- https://docutils.sourceforge.io/rst.html
- https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

### Sphinx

- _Documentation Generator_, der Textdateien von einem Format, z.B. `.rst`,
  in ein anderes Format überführt, z.B. _HTML_.
- seit 2008
- https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
- https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
- https://sphinx-tutorial.readthedocs.io
- https://sphinx-intro-tutorial.readthedocs.io
- https://www.sphinx-doc.org
- https://github.com/sphinx-doc/sphinx

### MkDocs

- Dokumentation in Markdown
- Default-Theme:
  - _Bootstrap_ 4.3.x https://getbootstrap.com als Frontend-Toolkit für "Responsiveness"
    (aktuell: 5.2)
  - _Font Awesome_ 4.7.x https://fontawesome.com als Icon-Bibliothek (aktuell: 6.3)
- _Material Design_ mit _Material Icons_ möglich
- genutzt für die Dokumentation von z.B. [FastAPI](#web--und-rest-frameworks),
  [Starlette](#asgi) und [uvicorn](#asgi)
- seit 2014
- ca. 21.000 Stars bei GitHub
- https://www.mkdocs.org
- https://github.com/mkdocs/mkdocs

### Generierung der Dokumentation mit MkDocs

```shell
    # Eingebauten Webserver starten
    uv run mkdocs serve

    # Webbrowser öffnen mit http://localhost:8000

    # Nur HTML-Dokumentation generieren
    uv run mkdocs build
```

Als Starthilfe zum Aufsetzen von _MkDocs_ gibt es das Kommando `mkdocs new .`,
um im aktuellen Verzeichnis die Konfigurationsdatei `mkdocs.yaml` und im
Unterverzeichnis `doc` die Datei `index.md` anzulegen.

## Web-Frameworks, ASGI und WSGI

### WSGI

_WSGI_ steht für _Web Server Gateway Interface_ und ist mit _Tomcat_ für Java oder
_Node_ für JavaScript vergleichbar. WSGI wurde urpsprünglich 2003 durch
https://peps.python.org/pep-0333 synchron spezifiziert und 2010 durch
https://peps.python.org/pep-3333 überarbeitet. Populäre WSGI Server sind z.B.:

- _Gunicorn_ (= Green Unicorn) https://flask.palletsprojects.com/en/2.2.x/deploying/gunicorn;
  verwendet z.B. bei _pgadmin_ und hervorgegangen aus _Unicorn_ von Ruby
- _uWSGI_ http://projects.unbit.it/uwsgi
- _Waitress_ https://docs.pylonsproject.org/projects/waitress
- _Flask Development Server_ mit "Code Reload": für synchrone Entwicklungsprojekte

### ASGI

Asynchrone Verarbeitung kann insbesondere bei I/O-intensiven Anwendungen
die Performance verbessern, z.B.:

- _Datenbank_-Zugriffe
- Email über einen _Mailserver_ verschicken
- Requests an _Web Services_, z.B. Google Maps, Instagram, Twitter, ...
- Zugriff auf _Identity Management Systeme_ (IDM), z.B. Keycloak von Red Hat
- Zugriff auf ERP-Systeme, z.B. von SAP oder SalesForce

Die Implementierung von asynchronen Anwendungen erfolgt in Python durch
_async/await_ seit Python 3.5 (2015) wie in JavaScript oder TypeScript.
Durch diese Einfachheit statt Callbacks (wie z.B. in _Express_) hat die Popularität
von asynchroner Entwicklung zugenommen: Beispielsweise hat der asynchrone Treiber
für PostgreSQL _asyncpg_ 6.700 Stars bei GitHub, während der synchrone Treiber
_psycopg_ nur 3.300 Stars hat. Die asynchronen DB-Treiber befolgen jedoch **nicht**
die Spezifikation _Python Database API Specification v2.0_ aus dem Jahr 1999.

_ASGI_ steht für _Asynchronous Server Gateway Interface_ und ist hervorgegangen
aus _Django Channels_. ASGI ist rückwärts-kompatibel mit WSGI: https://asgi.readthedocs.io
und https://groups.google.com/g/django-developers/c/ktTPNUTlsM0. Eine Sammlung von
ASGI-Servern- und Frameworks gibt es z.B. bei https://github.com/florimondmanca/awesome-asgi.
Zu ASGI gibt es übrigens **kein** PEP.

Implementierungen von ASGI sind vor allem:

- Daphne
  - Referenzimplementierung für ASGI
  - Teil von _Django Channels_
  - Nur in der Kommandozeile nutzbar und deshalb nicht programmatisch integrierbar
    mit _FastAPI_, um einfach `python -m kunde` aufrufen zu können
  - HTTP/2, WebSockets, uvm.
  - ca. 2.600 Stars bei GitHub
  - http://github.com/django/daphne
- uvicorn
  - einfach nutzbar
  - Reload des Codes möglich: deshalb auch interessant für Entwicklung
  - implementiert von Tom Christie, der auch _Django REST Framework_ implementierte
    und _Starlette_ (s.u.) sowie _MkDocs_ initiierte
  - oft verwendet, wenn _Flask_ asynchron genutzt wird
  - HTTP 1.1
  - ca. 10.200 Stars bei GitHub
  - https://www.uvicorn.org
  - https://github.com/encode/uvicorn
- Starlette
  - "The little ASGI _framework_ that shines"
  - Grundlage für das Web Framework [FastAPI](#web-frameworks-asgi-und-wsgi) (in Anlehnung an _Flask_)
  - initiiert von Tom Christie (siehe _uvicorn_)
  - Starlette, uvicorn, Django REST Framework und httpx sind bei https://github.com/encode
  - implementiert auch Routing, das in [FastAPI](#web-frameworks-asgi-und-wsgi) genutzt
    wird
  - seit 2020
  - ca. 11.800 Stars bei GitHub
  - https://www.starlette.io
  - https://github.com/encode/starlette
- Hypercorn
  - Grundlage für _Quart_: Reimplementierung des Web Frameworks [Flask](#web-frameworks-asgi-und-wsgi)
    vom gleichen Hersteller
  - Reload des Codes möglich: deshalb auch interessant für Entwicklung
  - HTTP 1.1, HTTP/2, HTTP/3 und WebSockets
  - seit 2019
  - ca. 1.500 Stars bei GitHub
  - https://github.com/pgjones/hypercorn

### Web- und REST-Frameworks

Eine Übersicht über diverse Python-basierte Web-Frameworks findet man unter
https://dzone.com/articles/python-web-frameworks-everything-you-need-to-know.
Diese Web-Frameworks sind vergleichbar mit _Spring Web MVC_ für Java sowie
_Nest_ und _Express_ für JavaScript bzw. TypeScript. Für alle etablierten
Frameworks kann man REST-Schnittstellen implementieren und es gibt außerdem
eine Integration mit z.B. _Strawberry_ oder _Graphene_, um eine
GraphQL-Schnittstelle zu implementieren.

- Django
  - genutzt von Delivery Hero, Instagram, Pinterest, ...
  - 2005 erstes Release
  - mehr als nur ein Web-Framework
  - enthält eine _Template-Engine_ für server-seitiges HTML
  - enthält django.db für _OR-Mapping_
  - enthält _Authentifizierung_ und _Autorisierung_
  - ursprünglich synchron
  - asynchron durch _Django Channels_
  - ca 86.300 Stars bei GitHub
  - https://www.djangoproject.com
  - https://github.com/django/django
  - https://code.visualstudio.com/docs/python/tutorial-django
- Django REST framework
  - REST-Schnittstelle auf Basis von Django
  - ursprünglich implementiert von Tom Christie, der auch [Starlette](#asgi) und
    [MkDocs](#mkdocs) initiierte
  - ca. 29.800 Stars bei GitHub
  - https://www.django-rest-framework.org
  - https://github.com/encode/django-rest-framework
- FastAPI
  - genutzt von u.a. Netflix für "Dispatch" (Werkzeug für "Crisis Management")
  - Entwicklung seit Dez. 2018
  - inspiriert durch _Nest_ (JavaScript), welches wiederum durch Spring inspiriert
    ist, sowie _Flask_
  - Dependency Injection
  - vor allem für REST-Schnittstellen
  - Routing auf Basis von [Starlette](#asgi) und damit asynchron durch die Nutzung
    von _AIOHTTP_ für HTTP 1.1, HTTP/2, HTTP/3
  - [OR-Mapping](#or-mapping) durch z.B. _SQLAlchemy_ oder _SQLModel_
  - nutzt [Pydantic](#validierung) zur Validierung, Serialisierung und Dokumentation
  - ca. 93.600 Stars bei GitHub
  - https://fastapi.tiangolo.com
  - https://github.com/tiangolo/fastapi
- Flask
  - genutzt von LinkedIn, Netflix, Uber, Zalando, locust, ...
  - _Microframework_
  - 2010 erstes Release als konfigurierbarer Gegenentwurf zu _Django_
  - **keine** vorkonfigurierte Integration für:
    - Template-Engine für HTML, z.B. _Jinja2_
    - OR-Mapping, z.B. [SQLAlchemy](#or-mapping)
    - Validierung, z.B. [Pydantic](#validierung) oder [Marshmallow](#validierung)
    - GraphQL, z.B. [Strawberry](#graphql) oder [Graphene](#graphql)
    - Authentifizierung und Autorisierung
  - ursprünglich synchron
  - asynchron durch Integration mit [uvicorn](#asgi) oder [hypercorn](#asgi)
    (HTTP 1.1, HTTP/2, HTTP/3)
  - Wird bei Docker als Beispiel für Python verwendet https://docs.docker.com/language/python/build-images
  - 71.^000 Stars bei GitHub
  - https://flask.palletsprojects.com
  - https://github.com/pallets/flask
  - https://code.visualstudio.com/docs/python/tutorial-flask
- <s>Falcon</s>
  - eit 2012
  - https://github.com/falconry/falcon
- <s>Bottle</s>
  - seit 2014
  - https://github.com/bottlepy/bottle
- <s>Eve</s>
  - seit 2018
  - https://github.com/pyeve/eve
- <s>Pyramid</s>
  - seit 2010
  - https://github.com/Pylons/pyramid
- <s>Quart</s>
  - seit 2017
  - https://github.com/pallets/quart

## OR-Mapping

- SQLAlchemy
  - Oracle, SQL Server, PostgreSQL, MySQL, MariaDB, SQLite
  - ähnlich wie _Hibernate_ für Java
  - häufig genutzt mit [FastAPI](#web--und-rest-frameworks) und [Flask](#web--und-rest-frameworks)
  - ca. 11.300 Stars bei GitHub
  - https://www.sqlalchemy.org
  - https://github.com/sqlalchemy/sqlalchemy
- SQLModel
  - vor allem für [FastAPI](#web--und-rest-frameworks)
  - von Sebastián Ramírez (Autor von FastAPI)
  - kombiniert SQLAlchemy und Pydantic (für validierung), um durch gemeinsame Klassen
    eine einfache und schnelle Entwicklung mit FastAPI zu ermöglichen
  - seit 2021
  - 17.400 Stars bei GitHub
  - https://sqlmodel.tiangolo.com
  - https://github.com/fastapi/sqlmodel
- Peewee
  - Pattern _Active Record_; vgl.:
    - _Panache_ als Alternative zu _Hibernate_ in _Quarkus_ (Red Hat)
    - _Mongoose_ für den DB-Zugriff auf MongoDB bei Node-Anwendungen
  - _SQLAlchemy_ enthält mehr Features, vor allem um komplexe Queries zu erstellen
  - seit 2013
  - ca. 11.900 Stars bei GitHub
  - http://docs.peewee-orm.com
  - https://github.com/coleifer/peewee
- django.db
  - fest-verdrahtet in _Django_
  - Oracle, PostgreSQL, MySQL, MariaDB, SQLite
  - https://docs.djangoproject.com/en/4.2/ref/databases

## Validierung

- Pydantic
  - Objekte werden mit "Model"-Klassen definiert als Alternative zu @dataclass
  - "pydantic is primarily a parsing library, not a **validation library**"
    https://docs.pydantic.dev/usage/models
  - Validierungsfehler als JSON-Objekte mit Tupeln als Werte, z.B.
    `{'loc': ('email',), 'msg': 'value is not a valid email address', 'type': 'value_error.email'}`
  - genutzt von [FastAPI](#web--und-rest-frameworks)
  - Erweiterung für VS Code
  - Plugin für MyPy: wird konfiguriert in `pyproject.toml`
  - ca. 26.300 Stars bei GitHub
  - 700 Contributors
  - genutzt von 890.000 Projekten bei GitHub
  - https://docs.pydantic.dev
  - https://github.com/pydantic/pydantic
- Marshmallow
  - Schema-Definition für Validierung durch Klassen
  - Deserialisieren von Dictionaries in Anwendungs-Objekte und umgekehrt
  - https://marshmallow.readthedocs.io
  - https://github.com/marshmallow-code/marshmallow
- webargs
  - Schema zur Validierung als Dictionary mit Typen als Werte
  - hervorgegangen aus Marshmallow (s.o.)
  - https://webargs.readthedocs.io
  - https://github.com/marshmallow-code/webargs
- Cerberus
  - Schema-Definition als JSON-Objekt
  - https://python-cerberus.org
  - https://github.com/pyeve/cerberus

## GraphQL

- Strawberry
  - _code-first_ mit _data classes_
  - Als 1. Library im Handbuch von FastAPI erwähnt
  - Integration mit [Django](#web--und-rest-frameworks), [FastAPI](#web--und-rest-frameworks)
    und [Flask](#web--und-rest-frameworks)
  - moderner als Graphene (s.u.): Type Hints, auch asynchron
  - seit 2020
  - ca. 4.600 Stars bei GitHub
  - https://strawberry.rocks
  - https://github.com/strawberry-graphql/strawberry
- Graphene
  - _schema-first_ und _code-first_
  - Django-Graphene zur Integration mit [Django](#web--und-rest-frameworks)
  - seit 2016
  - ca. 8.200 Stars bei GitHub
  - http://graphene-python.org
  - https://github.com/graphql-python/graphene
- <s>Ariadne</s>
  - _schema-first_
  - seit 2018
  - ca. 2.300 Stars bei GitHub
  - https://ariadnegraphql.org
  - https://github.com/mirumee/ariadne

## DB-Server und DB-Browser

> Vor dem 1. Start von PostgreSQL muss man die Skripte `create-db-kunde.sql`
> und `create-schema-kunde.sql` aus dem Verzeichnis `extras\postgres\sql` nach
> `C:\Zimmermann\volumes\postgres\sql` kopieren und die Anleitung ausführen.
> Danach kopiert man die CSV-Dateien aus dem Verzeichnis `extras\postgres\csv`
> nach `C:\Zimmermann\volumes\postgres\csv\kunde`.

Vor dem Start des Appservers muss man den DB-Server und ggf. den DB-Browser starten.

```shell
    # Windows
    cd .\extras\compose\postgres

    # macOS / Linux
    cd ./extras/compose/postgres

    docker compose up
```

## Applikationsserver

### localhost, 127.0.0.1 und 0.0.0.0

- `localhost`: DNS-Name, der defaultmäßig 127.0.0.1 referenziert
- `127.0.0.1`: _Loopback Adresse_ des Rechners
- `0.0.0.0`: irgendeine IP-Adresse, die für den Rechner in `C:\Windows\System32\drivers\etc\hosts`
  (Windows) oder `/etc/hosts` (Unix und MacOS) zugewiesen wurde; wird bei Docker Images
  mit Docker Compose verwendet

### HTTPS

Für HTTPS bzw. TLS benötigt man einen privaten Schlüssel und ein Zertifikat.
Das Zertifikat für HTTPS bzw. TLS kann man mit _OpenSSL_ und der Erweiterung
_opensslutils_ für VS Code inspizieren. Man öffnet die PEM-Datei ("Privacy-Enhanced
Mail"), drückt die Funktionstaste `<F1>` und gibt dann in der Kommandopalette
_OpenSSL: Show OpenSSL Preview_ ein.

OpenSSL wird beispielsweise mitinstalliert, wenn man _Git_ installiert und
`PATH` entsprechend setzt. Zu beachten ist dabei, dass `...\Git\mingw64\bin` in PATH
ggf. das Original-Kommando `find` von Windows überschreibt. Deshalb ist in
`.vscode\settings.json` der Eintrag von `opensslutils.opensslPath` vorhanden
und kann entsprechend angepasst werden.

Statt eines selbst-signierten Zertifikats kann man auch ein Zertifikat von
_Let's Encrypt_ durch z.B. _acme-tiny_ https://github.com/diafygi/acme-tiny
verwenden.

### Serverstart

Durch das Kommando `uv run kunde` kann man den Server starten: siehe `project.scripts`
in `pyproject.toml`.

Defaultmäßig wird beim Serverstart _uvicorn_ als ASGI-Server verwendet.
Stattdessen kann auch _hypercorn_ verwendet werden, indem man in `kunde.toml`
bei `[kunde.asgi]` das Tag `server` auf den Wert `hypercorn` setzt. Der Server
hat dann die Basis-URL `https://localhost:8000`.

Die von _SQLAlchemy_ generierten SQL-Anweisungen werden mit _logging_ aus der
Python-Standardbibliothek protokolliert. Dadurch haben sie ein anderes Log-Format
als _loguru_ und fallen auch dementsprechend auf. Wenn man das Log-Format von
loguru auch bei SQLAlchemy haben möchte, so muss man den auskommentierten Code
in `src\kunde\repository\session.py` aktivieren.

## Docker Images, Container und Docker Compose

### Minimales Basis-Image

Für ein kleines Basis-Image gibt es z.B. folgende Alternativen:

- _Alpine_
  - C-Bibliothek _musl_ statt von GNU
  - _ash_ als Shell
  - _apk_ ("Alpine Package Keeper") als Package-Manager
- _Debian slim_

### Image erstellen

Durch eine Default-Datei `Dockerfile` kann man ein Docker-Image erstellen und
durch ein _Multi-stage Build_ optimieren. Eine weitverbreitete Namenskonvention
für ein Docker-Image ist `<registry-name>/<username>/<image-name>:<image-tag>`.
Ob das Dockerfile gemäß _Best Practices_ (https://docs.docker.com/develop/develop-images/dockerfile_best-practices)
erstellt wurde, kann man mit _Hadolint_ überprüfen.

Je nach Basis-Image kann man mit Dockerfile künfitg ein Image erstellen und zunächst mit
Hadolint validieren:

```shell
    # Docker Hardened Image
    Get-Content Dockerfile | docker run --rm --interactive hadolint/hadolint:v2.14.0-debian
    # Debian Trixie slim
    Get-Content Dockerfile.trixie | docker run --rm --interactive hadolint/hadolint:v2.14.0-debian
    # Alpine
    Get-Content Dockerfile.alpine | docker run --rm --interactive hadolint/hadolint:v2.14.0-debian
```

Mit Docker _Bake_ kann man nun ein Docker-Image erstellen:

```shell
    # Docker Hardened Image als default
    docker buildx bake
    docker buildx bake trixie
    docker buildx bake alpine
```

oder manuell:

```shell
    # Docker Hardened Image
    docker build --tag juergenzimmermann/kunde:2026.4.1-hardened .
    # Debian Trixie slim
    docker build --tag juergenzimmermann/kunde:2026.4.1-trixie --file Dockerfile.trixie .
    # Alpine
    docker build --tag juergenzimmermann/kunde:2026.4.1-alpine --file Dockerfile.alpine .
```

### Image inspizieren

#### docker history

Mit dem Unterkommando `history` kann man ein Docker-Image und die einzelnen Layer
inspizieren:

```shell
    docker history juergenzimmermann/kunde:2026.4.1-hardened
    docker history juergenzimmermann/kunde:2026.4.1-trixie
    docker history juergenzimmermann/kunde:2026.4.1-alpine
```

#### docker inspect

Mit dem Unterkommando `inspect` kann man die Metadaten, z.B. Labels, zu einem
Image inspizieren:

```shell
    docker inspect juergenzimmermann/kunde:2026.4.1-hardened
    docker inspect juergenzimmermann/kunde:2026.4.1-trixie
    docker inspect juergenzimmermann/kunde:2026.4.1-alpine
```

#### docker sbom

Mit dem Unterkommando `sbom` (Software Bill of Materials) von `docker` kann man
inspizieren, welche Bestandteile in einem Docker-Images enthalten sind, z.B.
Python-Wheels (.whl) oder Debian-Packages.

```shell
    docker sbom juergenzimmermann/kunde:2026.4.1-hardened
    docker sbom juergenzimmermann/kunde:2026.4.1-trixie
    docker sbom juergenzimmermann/kunde:2026.4.1-alpine
```

### Docker Compose

Mit _Docker Compose_ kann man die Anwendung kunde z.B. zusammen mit PostgreSQL
starten. Dazu ist der _Service_ `kunde` in der Datei `compose.yml` im Verzeichnis.
`extras\compose\kunde` unter Verwendung des Images so konfiguriert, dass er erst dann
gestartet wird, wenn der "healthcheck" des DB-Servers "ready" meldet. Als Image wird
das Image auf Basis von _Debian Bookworm_ (Debian 12) verwendet. Alternativ kann das
Image auf Basis von _Alpine_ verwendet werden (siehe Kommentar in compose.yml).

Der Appserver ist defaultmäßig mit dem ASGI-Produkt _uvicorn_ konfiguriert. Wenn man
stattdessen _hypercorn_ für ASGI verwenden möchte, so setzt man in `extras\compose\kunde\kunde.toml`
im Block `kunde.asgi` beim Schüssel `server` den Wert `hypercorn`.

```shell
    # Windows
    cd extras\compose\kunde
    # macOS / Linux
    cd extras/compose/kunde

    # Voraussetzung: Keycloak als Container ist separat gestartet
    # Shell fuer kunde zzgl. DB-Server und Mailserver
    # kunde mit Basis-Image Debian Trixie (Hardened Image ohne Shell, Alpine mit ash siehe Kommentar)
    docker compose up

    # Nur zur Fehlersuche: weitere Shell für bash
    # Windows
    cd extras\compose\kunde
    # macOS / Linux
    cd extras/compose/kunde

    docker compose exec kunde bash
        id
        env
        exit

    # Fehlersuche im Netzwerk:
    docker compose -f compose.busybox.yml up
    docker compose exec busybox sh
        nslookup postgres
        exit

    # 2. Powershell: Server herunterfahren einschl. DB-Server und Mailserver
    cd extras\compose\kunde
    docker compose down
```

Um die virtuellen Server wieder zu beenden ruft man in einer 2. PowerShell das analoge
Kommando mit `down` statt `up` auf.

## Statische Codeanalyse

### Statische Codeanalyse im Überblick

Quellen:

- https://awesome-python.com/#code-analysis
- https://realpython.com/python-code-quality/#linters
- https://books.agiliq.com/projects/essential-python-tools/en/latest/linters.html

Übersicht:

- ruff
  - seit 2022 von Astral
  - Funktionalität der Linter (Flake8, isort, Pylint, pycodestyle, pyupgrade, refurb, ...),
    des Formatierers Black sowie für die Prüfung auf Sicherheitslücken durch Bandit
  - 800+ Regeln
  - implementiert in Rust
  - 10-100x schneller als die Originale
  - Konfiguration in pyproject.toml
  - Erweiterung für VS Code
  - genutzt bei der Entwicklung von z.B. FastAPI, pydantic, pytest, pip, MyPy, Pylint,
    pandas, Polars
  - ca. 44.900 Stars bei GitHub
  - https://github.com/astral-sh/ruff
  - https://realpython.com/ruff-python
- ty
  - Type Checker
  - seit 2025 von Astral (wie ruff)
  - implementiert in Rust
  - Plugin für VS Code vorhanden
  - ca. 16.000 Stars bei GitHub
  - https://github.com/astral-sh/ty
  - https://docs.astral.sh/ty
- SonarQube
  - ca. 30 unterstützte Programmiersprachen
  - z.B. Java, JavaScript, TypeScript, Python, Kotlin, Swift, PL/SQL, HTML, CSS, Cobol
  - Integration mit Ticketsystemen, wie z.B. JIRA
  - https://www.sonarsource.com/products/sonarqube
- pyright
  - von Microsoft
  - implementiert in TypeScript für Pylance als Erweiterung für VS Code
  - deshalb Installation mit npm
  - https://github.com/microsoft/pyright
- pyre-check
  - von Meta
  - nur für Linux und MacOS
  - https://pyre-check.org
- pyrefly
  - Type Checker
  - von Meta wie pyre-check
  - implementiert in Rust wie ruff und ty von Astral
  - http://pyrefly.org
- mypy
  - http://www.mypy-lang.org
- pylint
  - PyCQA = Python Code Quality Authority
  - Plugins für Django (Web Framework) und pydantic (data classes)
  - https://pylint.readthedocs.io
- flake8
  - PyCQA = Python Code Quality Authority
  - https://github.com/PyCQA/flake8

### ruff

Durch `uvx ruff check src` wird der Quellcode hinsichtlich _Type Hints_ analysiert,
wobei die Regeln aus _Flake8_ und _isort_ angewandt werden. Durch `uvx ruff format src`
wird _ruff_ verwendet, um die Verletzungen in den diversen Dateien neu zu formatieren.

### SonarQube

Für eine statische Codeanalyse durch _SonarQube_ muss zunächst der
SonarQube-Server mit _Docker Compose_ als Docker-Container gestartet werden:

```shell
    # Windows
    cd extras\compose\sonarqube
    # macOS / Linux
    cd extras/compose/sonarqube

    docker compose up
```

Wenn der Server zum ersten Mal gestartet wird, ruft man in einem Webbrowser die
URL `http://localhost:9000` auf. In der Startseite muss man sich einloggen und
verwendet dazu als Loginname `admin` und ebenso als Password `admin`. Danach
wird man weitergeleitet, um das initiale Passwort zu ändern.

Nun wählt man in der Webseite rechts oben das Profil über _MyAccount_ aus und
klickt auf den Karteireiter _Security_. Im Abschnitt _Generate Tokens_ macht man
nun die folgende Eingaben:

- _Name_: z.B. Frameworks für Python
- _Type_: _Global Analysis Token_ auswählen
- _Expires in_: z.B. _90 days_ auswählen

Abschließend klickt man auf den Button _Generate_ und trägt den generierten
Token in der Datei `sonar-project.properties` für die Property `sonar.token` ein,
damit der Token im Skript `sonar-scanner.py` verwendet werden kann.

Nachdem der Server gestartet ist, wird der SonarQube-Scanner in einer zweiten
PowerShell mit `python sonar-scanner.py` gestartet. Das Resultat kann dann in der
Webseite des zuvor gestarteten Servers über die URL `http://localhost:9000`
inspiziert werden.

Abschließend wird der oben gestartete Server in einer 2. PowerShell heruntergefahren.

```shell
    # Windows
    cd extras\compose\sonarqube
    # macOS / Linux
    cd extras/compose/sonarqube

    docker compose down
```

## Code Formatter

Ähnliche Funktionalität wie Prettier für JavaScript und TypeScript. Es empfiehlt
sich **nur einen** Code Formatter zu installieren. In `.vscode\settings.json` ist
konfiguriert, welcher Code Formatter von VS Code beim Abspeichern verwendet wird.

### ruff statt Black

- Funktionalität der Linter (Flake8, isort, pydocstyle, ...), des Formatierers Black
sowie für die Prüfung auf Sicherheitslücken durch Bandit
- 800+ Regeln
- implementiert in Rust
- 10-100x schneller als die Originale
- Konfiguration in pyproject.toml
- Erweiterung für VS Code
- 44.900 Stars bei GitHub
- https://github.com/astral-sh/ruff

### black

- von der _Python Software Foundation_ (PSF)
- https://black.readthedocs.io

### autopep8

- enthalten in der Erweiterung Pylance für VS Code
- https://github.com/hhatto/autopep8

### YAPF

- von Google
- Styles: pep8, google, facebook
- https://github.com/google/yapf

### isort

- Sortieren der import-Klauseln
- https://github.com/PyCQA/isort

## Analyse für Sicherheitslücken

### OWASP Dependency Check

Mit _OWASP Dependency Check_ werden alle in `pyproject.toml` installierten
Module mit den _CVE_-Nummern der NIST-Datenbank abgeglichen.

Von https://nvd.nist.gov/developers/request-an-api-key fordert man einen "API Key"
an, um im Laufe des Semesters mit _OWASP Dependency Check_ die benutzte Software
("3rd Party Libraries") auf Sicherheitslücken zu prüfen. Diesen API Key trägt
man im Skript `extras\dependency-check.py` als Wert der Variablen `nvd_api_key` ein.

```shell
    uv run extras/dependency-check.py
```

### ruff statt Bandit

_ruff_ implementiert auch die Regeln von _Bandit_.

### Sicherheitslücken in 3rd Party Packages

Zur Überprüfung von bekannten Sicherheitslücken in den verwendeten 3rd Party Packages
bietet uv (noch) keine Lösung, die mit z.B. `npm audit` bei JavaScript vergleichbar ist:
https://github.com/astral-sh/uv/issues/9189.

Als Alternative kann man zwischenzeitlich das Standalone-Werkzeug _pysentry-rs_ oder
_pip-audit_ für _pip_verwenden:

```shell
    uvx pysentry-rs

    # pip-audit kann nur requirements.txt analysieren, aber nicht pyproject.toml
    uv pip compile pyproject.toml > requirements.txt
    uvx pip-audit -r requirements.txt
```

### Docker Scout

Mit dem Unterkommando `quickview` von _Scout_ kann man sich zunächst einen
groben Überblick verschaffen, wieviele Sicherheitslücken in den Bibliotheken im
Image enthalten sind:

```shell
    docker scout quickview juergenzimmermann/kunde:2026.4.1-hardened
    docker scout quickview juergenzimmermann/kunde:2026.4.1-trixie
    docker scout quickview juergenzimmermann/kunde:2026.4.1-alpine
```

Dabei bedeutet:

- C ritical
- H igh
- M edium
- L ow

Sicherheitslücken sind als _CVE-Records_ (CVE = Common Vulnerabilities and Exposures)
katalogisiert: https://www.cve.org (ursprünglich: https://cve.mitre.org/cve).
Die Details zu den CVE-Records im Image kann man durch das Unterkommando `cves`
von _Scout_ auflisten:

```shell
    docker scout cves juergenzimmermann/kunde:2026.4.1-hardened
    docker scout cves --format only-packages juergenzimmermann/kunde:2026.4.1-hardened
```

Statt der Kommandozeile kann man auch den Menüpunkt "Docker Scout" im
_Docker Dashboard_ verwenden.

## Testen

### pytest statt unittest

_pytest_ https://docs.pytest.org ist eine bessere Alternative zu _unittest_ aus der
Python-Distribution.

### HTTP-Client für Integrationstests

- Requests
  - genutzt in 2,5 Mio Projekten bei GitHub
  - ca. 53.700 Stars bei GitHub
  - nutzt Flask zur Entwicklung
  - https://requests.readthedocs.io
  - https://github.com/psf/requests
- httpx
  - API weitestgehend kompatibel mit _Requests_
  - HTTP/2
  - Asynchroner Client
  - genutzt für den Testclient von Starlette und deshalb auch FastAPI seit 2022
  - genutzt in 545.000 Projekten bei GitHub
  - ca. 15.000 Stars bei GitHub
  - https://www.python-httpx.org
  - https://github.com/encode/httpx
- urllib3
  - genutzt in 2,4 Mio Projekten bei GitHub
  - ca. 4.000 Stars bei GitHub
  - https://urllib3.readthedocs.io
  - https://github.com/urllib3/urllib3

### Backend-Server und Appserver als Voraussetzung für Integrationstests

Vor dem Start der Integrationstests müssen DB-Server, Keycloak-Server und Appserver
gestartet sein. Der Mailserver sollte gestartet sein.

Die Integrationstests sind unterhalb von `tests` in den Verzeichnissen
`graphql_api`, `rest` und `security`. Durch jeweils ein _Fixture_ von pytest werden
pro Verzeichnis die (Test-) Datenbank und _Keycloak_ neu geladen.

### pytest in der Kommandozeile

Durch `pytest` werden die Tests im Verzeichnis `tests` ausgeführt, weil das
Verzeichnis `tests` in `pyproject.toml` als Test-Verzeichnis deklariert ist.
Durch `uv run pytest --co` ("collect-only") kann man sich auflisten lassen, in
welcher Reihenfole die Tests ausgeführt werden.

Mit der Option `--cache-clear` kann man den Cache von pytest leeren.

Mit z.B. `uv run pytest -m get_request` startet man nur Test mit der Markierung
`get_request` oder man verwendet in `pyproject.toml` bei der Table `[tool.pytest.ini_options]`
die Property `addopts`.

### pytest mit VS Code

Zunächst klickt man in der Werkzeugleiste (am linken Rand) auf das _test beaker icon_,
das aussieht wie ein Becherglas bei einem chemischen Versuch, und klickt danach
auf den Menüpunkt _Configure Python Tests_. Nun wählt man der Reihe nach _pytest_
und _tests_ aus. Jetzt kann man die gewünchte(n) Testfunktion auswählen und
einschließlich der Fixtures starten.

Weitere Details siehe auch https://code.visualstudio.com/docs/python/testing.

### locust für Lasttests

Siehe `README.md` in `tests\lasttest`.

### Port bereits belegt?

Falls der Server nicht gestartet werden kann, weil z.B. der Port `3000` belegt ist,
kann man bei Windows in der Powershell zunächst die ID vom Betriebssystem-Prozess ermitteln,
der den Port belegt und danach diesen Prozess beenden:

```powershell
    netstat -ano | findstr ':3000'
    taskkill /F /PID <Prozess-ID>
```

Bei macOS:

```shell
    ps -af
    kill <Prozess-ID>
    # ggf.
    kill -9 <Prozess-ID>
```

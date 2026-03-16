# Hinweise zu AsciiDoctor und PlantUML

<!--
  Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.
-->

[Juergen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de)

Mit AsciiDoctor und PlantUML ist die Dokumentation geschrieben.

## Preview von PlantUML-Dateien

Um in VS Code die Erweiterung für PlantUML zu nutzen, wird eine Java-Installation
benötigt, d.h. die Umgebungsvariable `JAVA_HOME` muss auf das Wurzelverzeichnis
der Java-Installation verweisen und die Umgebugnsvariable `PATH` muss dieses
Verzeichnis einschließlich dem Unterverzeichnis `bin` enthalten.

Durch das Tastaturkürzel `<Alt>d` erhält man eine Preview-Sicht vom jeweiligen
UML-Diagramm. Dazu ist eine Internet-Verbindung notwendig.

## Einstellungen für Preview von AsciiDoctor-Dateien

Zunächst müssen einmalig die Einstellungen (_Settings_) von VS Code geändert
werden. Dazu klickt man in der linken unteren Ecke das Icon ("Rädchen") für die
Einstellungen an und wählt den Menüpunkt _Einstellungen_ bzw. _Settings_ aus.
Dann gibt man im Suchfeld `asciidoc.use_kroki` ein und setzt den Haken bei
_Enable kroki integration to generate diagrams_.

Wenn man zum ersten Mal eine `.adoc`-Datei im Editor öffnet, muss man noch
die Verbindung zum PlantUML-Server zulassen, damit die eingebundenen
`.plantuml`-Dateien in `.svg`-Dateien konvertiert werden. Dazu gibt man zunächst
`<F1>` ein und schickt im Eingabefeld das Kommando
_AsciiDoc: Change Preview Security Settings_ durch `<Enter>` ab.
Danach wählt man den Unterpunkt _Allow insecure content_ aus.

## Preview von AsciiDoctor-Dateien

Durch das Tastaturkürzel `<Strg><Shift>v` erhält man die Preview-Ansicht.
Dazu ist eine Internet-Verbindung notwendig.

## Gesamte Dokumentation mit mkdocs

Um den Webserver von _mkdocs_ zu starten, ruft man `uv run mkdocs serve` auf.
Danach kann man den Webbrowser mit `http://localhost:8000` öffnen.

Wenn man nur die HTML-Dokumentation generieren möchte, genügt der Befehl
`uv run mkdocs build`.

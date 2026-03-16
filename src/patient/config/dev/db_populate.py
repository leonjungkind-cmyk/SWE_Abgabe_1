# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Neuladen der DB im Modus DEV."""

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from re import match
from string import Template
from typing import Final

from loguru import logger
from sqlalchemy import Connection, create_engine, text

from patient.config.config import resources_path
from patient.config.db import (
    db_connect_args,
    db_dialect,
    db_log_statements,
    db_url_admin,
)
from patient.config.dev_modus import dev_db_populate
from patient.repository import engine

__all__ = ["DbPopulateService", "db_populate", "get_db_populate_service"]


utf8: Final = "utf-8"
# https://docs.python.org/3/library/importlib.resources.htm
# https://docs.python.org/3/whatsnew/3.9.html#importlib
_db_traversable: Final[Traversable] = files(resources_path)


# logging.basicConfig(handlers=[LogInterceptHandler()], level=0)  # NOSONAR
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)


class DbPopulateService:
    """Neuladen der DB im Modus DEV."""

    def __init__(self) -> None:
        """Initialisierung von `Engine` für SQLAlchemy mit dem Admin-User."""
        self.engine_admin: Final = (
            create_engine(
                db_url_admin,
                connect_args=db_connect_args,
                echo=db_log_statements,
            )
            if db_dialect == "postgresql"
            else create_engine(db_url_admin, echo=db_log_statements)
        )

    # DB-Migration ggf. durch Alembic https://alembic.sqlalchemy.org
    def populate(self) -> None:
        """DB durch einzelne SQL-Anweisungen als Prepared Statement neu laden."""
        if not dev_db_populate:
            return

        logger.warning(">>> Die DB wird neu geladen: {} <<<", engine.url)
        connection: Connection
        with engine.connect() as connection:
            db_dialect: Final = connection.dialect.name
            dialect_path: Final = _db_traversable / db_dialect
            with Path(str(dialect_path / "drop.sql")).open(encoding=utf8) as drop_sql:
                zeilen_drop: Final = self._remove_comment(drop_sql.readlines())
                drop_statements: Final = self._build_sql_statements(zeilen_drop)
                for stmt in drop_statements:
                    connection.execute(text(stmt))
            with Path(str(dialect_path / "create.sql")).open(
                encoding=utf8
            ) as create_sql:
                zeilen_create: Final = self._remove_comment(create_sql.readlines())
                create_statements: Final = self._build_sql_statements(zeilen_create)
                for stmt in create_statements:
                    connection.execute(text(stmt))
            connection.commit()
        engine.dispose()
        self._load_csv_files()
        logger.warning(">>> Die DB wurde neu geladen <<<")

    def _remove_comment(self, zeilen: list[str]) -> list[str]:
        """SQL-Kommentare und Leerzeilen entfernen."""
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        return [
            zeile for zeile in zeilen if not match(r"^ *--", zeile) and zeile != "\n"
        ]

    def _build_sql_statements(self, zeilen: list[str]) -> list[str]:
        """Zeilen mit SQL-Anweisungen zu einer Zeile zusammenfassen."""
        statements: list[str] = []
        sql: str = ""
        anzahl: Final = len(zeilen)
        for i in range(anzahl):
            zeile = zeilen[i]
            sql += zeile.replace("\n", " ")
            if zeile.endswith(";\n"):
                statements.append(sql)
                sql = ""
        return statements

    def _load_csv_files(self) -> None:
        logger.debug("begin")
        tabellen: Final = ["patient", "adresse", "rechnung"]
        csv_path: Final = "/init/patient/csv"
        # siehe extras/compose/postgres/compose.init.yml
        with self.engine_admin.connect() as connection:
            connection.execute(text("SET search_path TO patient;"))
            for tabelle in tabellen:
                self._load_csv_file(
                    tabelle=tabelle,
                    csv_path=csv_path,
                    connection=connection,
                )
                connection.commit()
        self.engine_admin.dispose()

    # Alternative zu COPY (PostgreSQL): pandas.load_csv() angeblich 5-7x langsamer
    # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    # polars.read_csv() angeblich bis zu 10x schneller als Pandas
    # + Rust als Implementierungssprache einschl. "Safe Concurrency"
    # + Apache Arrow als effizientes Speicherformat
    # https://docs.pola.rs/api/python/stable/reference/api/polars.read_csv.html
    def _load_csv_file(
        self, tabelle: str, csv_path: str, connection: Connection
    ) -> None:
        logger.debug("tabelle={}", tabelle)
        copy_cmd: Final = Template(
            "COPY ${TABELLE} FROM '"
            + csv_path
            + "/${TABELLE}.csv' (FORMAT csv, QUOTE '\"', DELIMITER ';', HEADER true);",
        ).substitute(TABELLE=tabelle)
        connection.execute(text(copy_cmd))


def get_db_populate_service() -> DbPopulateService:
    """Factory-Funktion für DbPopulateService."""
    return DbPopulateService()


def db_populate():
    """DB mit Testdaten neu laden, falls im dev-Modus."""
    if dev_db_populate:
        service = get_db_populate_service()
        service.populate()

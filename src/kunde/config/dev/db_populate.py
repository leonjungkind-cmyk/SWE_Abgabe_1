"""Neuladen der DB im Modus DEV."""

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from re import match
from string import Template
from typing import Final

from loguru import logger
from sqlalchemy import Connection, create_engine, text

from kunde.config.config import resources_path
from kunde.config.db import (
    db_connect_args,
    db_dialect,
    db_log_statements,
    db_url_admin,
)
from kunde.config.dev_modus import dev_db_populate
from kunde.repository import engine

__all__ = ["DbPopulateService", "db_populate", "get_db_populate_service"]


utf8: Final = "utf-8"
_db_traversable: Final[Traversable] = files(resources_path)


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

    def populate(self) -> None:
        """DB durch einzelne SQL-Anweisungen als Prepared Statement neu laden."""
        if not dev_db_populate:
            return

        logger.warning(">>> Die DB wird neu geladen: {} <<<", engine.url)

        with engine.connect() as connection:
            connection.execute(text("SET search_path TO kunde;"))

            dialect_name: Final = connection.dialect.name
            dialect_path: Final = _db_traversable / dialect_name

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
        return [
            zeile for zeile in zeilen if not match(r"^ *--", zeile) and zeile != "\n"
        ]

    def _build_sql_statements(self, zeilen: list[str]) -> list[str]:
        """Zeilen mit SQL-Anweisungen zu einer Zeile zusammenfassen."""
        statements: list[str] = []
        sql = ""

        for zeile in zeilen:
            sql += zeile.replace("\n", " ")
            if zeile.endswith(";\n"):
                statements.append(sql)
                sql = ""

        return statements

    def _load_csv_files(self) -> None:
        """CSV-Dateien in die Tabellen laden."""
        logger.debug("begin")
        tabellen: Final = ["kunde", "adresse", "bestellung"]
        csv_path: Final = "/init/kunde/csv"

        with self.engine_admin.connect() as connection:
            connection.execute(text("SET search_path TO kunde;"))

            for tabelle in tabellen:
                self._load_csv_file(
                    tabelle=tabelle,
                    csv_path=csv_path,
                    connection=connection,
                )
                connection.commit()

        self.engine_admin.dispose()

    def _load_csv_file(
        self, tabelle: str, csv_path: str, connection: Connection
    ) -> None:
        """Eine CSV-Datei per COPY in die jeweilige Tabelle laden."""
        logger.debug("tabelle={}", tabelle)

        copy_cmd: Final = Template(
            "COPY ${TABELLE} FROM '"
            + csv_path
            + "/${TABELLE}.csv' (FORMAT csv, QUOTE '\"', DELIMITER ',', HEADER match);"
        ).substitute(TABELLE=tabelle)

        connection.execute(text(copy_cmd))


def get_db_populate_service() -> DbPopulateService:
    """Factory-Funktion für DbPopulateService."""
    return DbPopulateService()


def db_populate() -> None:
    """DB mit Testdaten neu laden, falls im Dev-Modus."""
    if dev_db_populate:
        service = get_db_populate_service()
        service.populate()

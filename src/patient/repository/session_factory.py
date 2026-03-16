# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Asynchrone Engine und die Factory für asynchrone Sessions konfigurieren."""

from typing import Final

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from patient.config.db import (
    db_connect_args,
    db_log_statements,
    db_url,
)

__all__ = ["Session", "engine"]

# https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
# isolation_level= "SERIALIZABLE","REPEATABLE READ","READ COMMITTED","READ UNCOMMITTED"
# Default Isolation Level "READ COMMITTED": Schreibsperren und keine Lesesperren
# https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#transaction-isolation-level
# https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-DEFAULT-TRANSACTION-ISOLATION
# pool_size=5
engine: Final = create_engine(
    db_url,
    connect_args=db_connect_args,
    echo=db_log_statements,
)
"""'Engine' für SQLAlchemy, um DB-Verbindungen und Sessions zu erstellen."""

logger.info("Engine fuer SQLAlchemy erzeugt")


# https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
# https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.params.expire_on_commit
# https://groups.google.com/g/sqlalchemy/c/uYIawg4SUQQ
Session = sessionmaker(bind=engine, autoflush=False)
"""Factory für Sessions, um generierte SQL-Anweisungen in Transaktionen abzusetzen."""

logger.info("Session-Factory fuer SQLAlchemy erzeugt")

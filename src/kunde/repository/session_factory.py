"""Session-Factory für die Datenbank."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kunde.config.db import db_connect_args, db_url

__all__ = ["Session", "engine"]

engine = create_engine(
    db_url,
    connect_args=db_connect_args,
    echo=False,
)

Session = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

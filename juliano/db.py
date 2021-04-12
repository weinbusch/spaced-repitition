import logging

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import event


db_logger = logging.getLogger("sqlalchemy.engine")
db_logger.setLevel(logging.INFO)


def activate_sqlite_fk_constraints(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine(path):
    e = create_engine(path)
    event.listen(e, "connect", activate_sqlite_fk_constraints)
    return e


def connect(path):
    """Connect to engine and create a session"""
    engine = get_engine(path)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


def disconnect(session):
    session.close()


@contextmanager
def session_scope():
    session = connect()
    yield session
    disconnect(session)

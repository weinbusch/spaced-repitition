import logging

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy import event


DB_PATH = "sqlite:///juliano.db"


db_logger = logging.getLogger("sqlalchemy.engine")
db_logger.setLevel(logging.INFO)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(DB_PATH)


def get_engine():
    return engine


def connect():
    """ Create a session """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


def disconnect(session):
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@contextmanager
def session_scope():
    session = connect()
    yield session
    disconnect(session)

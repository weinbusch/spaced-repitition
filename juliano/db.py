from flask import current_app, g
from werkzeug.local import LocalProxy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import event

from juliano.repo import UserRepository, ItemRepository


class Session:
    """Session

    A wrapper around sqlalchemy `session' with additional pointers to
    various repositories.

    """

    def __init__(self, path):
        self.session = connect(path)
        self.users = UserRepository(self.session)
        self.items = ItemRepository(self.session)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def disconnect(self):
        self.session.close()


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


def get_db():
    if "_db" not in g:
        g._db = Session(current_app.config["DB_PATH"])
    return g._db


db_session = LocalProxy(get_db)

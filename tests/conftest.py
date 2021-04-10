import logging

from unittest.mock import patch

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from juliano.app import app
from juliano.models import Base, User


@pytest.fixture(scope="session")
def engine():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.NOTSET)
    e = create_engine("sqlite:///:memory:")
    with patch("juliano.db.get_engine") as get_engine:
        get_engine.return_value = e
        yield e
    e.dispose()


@pytest.fixture
def database(engine):
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(database):
    session_factory = sessionmaker(bind=database)
    Session = scoped_session(session_factory)
    yield Session
    Session.remove()


@pytest.fixture()
def superuser(session):
    user = User(id=1, username="foo")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def flask_app(database):
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "test.localdomain"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["DB_PATH"] = "sqlite:///:memory:"
    app.config["REGISTER_VIEW"] = True
    with app.app_context():
        yield app


@pytest.fixture
def flask_anonymous_client(flask_app):
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def flask_client(flask_anonymous_client, superuser):
    with flask_anonymous_client.session_transaction() as sess:
        sess["_user_id"] = superuser.get_id()
        sess["_fresh"] = True
    return flask_anonymous_client

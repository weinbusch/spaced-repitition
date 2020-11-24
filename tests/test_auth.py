import pytest

from flask import url_for

from juliano.models import User
from juliano.auth import generate_password_hash, get_authenticated_user


@pytest.fixture(scope="module")
def password_hash():
    yield generate_password_hash("password")


def test_login_with_correct_credentials(flask_anonymous_client, session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    response = flask_anonymous_client.post(
        url_for("login"), data={"username": "foo", "password": "password"}
    )

    assert response.status_code == 302


def test_login_with_wrong_username(flask_anonymous_client, session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    response = flask_anonymous_client.post(
        url_for("login"), data={"username": "bar", "password": "password"}
    )

    assert response.status_code == 200


def test_login_with_wrong_password(flask_anonymous_client, session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    response = flask_anonymous_client.post(
        url_for("login"), data={"username": "foo", "password": "wrong-password"}
    )

    assert response.status_code == 200


def test_login_with_long_password(flask_anonymous_client, session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    response = flask_anonymous_client.post(
        url_for("login"), data={"username": "foo", "password": "a" * 65}
    )

    assert response.status_code == 200


def test_get_authenticated_user(session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    authenticated_user = get_authenticated_user(
        session, username="foo", password="password"
    )

    assert authenticated_user == user


def test_get_authenticated_user_wrong_password(session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    authenticated_user = get_authenticated_user(
        session, username="foo", password="wrong-password"
    )

    assert authenticated_user is None


def test_get_authenticated_user_long_password(session, password_hash):
    user = User(username="foo", password_hash=password_hash)
    session.add(user)
    session.commit()

    authenticated_user = get_authenticated_user(
        session, username="foo", password="a" * 65
    )

    assert authenticated_user is None

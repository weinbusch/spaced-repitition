import datetime

import pytest

from flask import url_for

from juliano.auth import (
    User,
    generate_password_hash,
    get_authenticated_user,
    get_user_from_token,
)


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


def test_register_user(flask_anonymous_client, session):
    response = flask_anonymous_client.post(
        url_for("register"),
        data={
            "username": "foo",
            "password": "password",
            "repeat_password": "password",
        },
    )
    assert response.status_code == 302
    assert session.query(User).first().username == "foo"


def test_register_view_opt_out(flask_anonymous_client):
    flask_anonymous_client.application.config["REGISTER_VIEW"] = False
    response = flask_anonymous_client.get(url_for("register"))
    assert response.status_code == 404
    response = flask_anonymous_client.post(
        url_for("register"),
        data={"username": "foo", "password": "bar", "repeat_password": "bar"},
    )
    assert response.status_code == 404


def test_register_existing_username(flask_anonymous_client, session):
    session.add(User(username="foo"))
    session.commit()

    response = flask_anonymous_client.post(
        url_for("register"),
        data={
            "username": "foo",
            "password": "password",
            "repeat_password": "password",
        },
    )
    assert response.status_code == 200
    assert b"Dieser Name existiert bereits." in response.data


def test_register_password_mismatch(flask_anonymous_client):
    response = flask_anonymous_client.post(
        url_for("register"),
        data={
            "username": "foo",
            "password": "password",
            "repeat_password": "wrong-password",
        },
    )
    assert response.status_code == 200
    assert "Die Passwörter müssen übereinstimmen".encode("utf-8") in response.data


def test_register_long_username(flask_anonymous_client):
    response = flask_anonymous_client.post(
        url_for("register"),
        data={
            "username": "f" * 100,
            "password": "password",
            "repeat_password": "password",
        },
    )
    assert response.status_code == 200
    assert "Dieser Name ist zu lang".encode("utf-8") in response.data


def test_register_long_password(flask_anonymous_client):
    response = flask_anonymous_client.post(
        url_for("register"),
        data={"username": "foo", "password": "p" * 65, "repeat_password": "p" * 65},
    )
    assert response.status_code == 200
    assert "Das Passwort ist zu lang".encode("utf-8") in response.data


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


def test_get_token():
    user = User()
    user.get_token()
    assert user.token is not None
    assert user.token_expires is not None


def test_get_expired_token():
    now = datetime.datetime.utcnow()
    user = User()
    t1 = user.get_token()
    user.token_expires = now - datetime.timedelta(seconds=1)
    t2 = user.get_token()
    assert t1 != t2
    assert t2 == user.token


def test_get_user_from_token(session):
    user = User()
    user.get_token()
    session.add(user)
    session.commit()

    assert get_user_from_token(session, user.token) == user


def test_get_user_from_wrong_token(session):
    user = User()
    user.get_token()
    session.add(user)
    session.commit()

    assert get_user_from_token(session, "foo") is None


def test_get_user_from_expired_token(session):
    now = datetime.datetime.utcnow()

    user = User()
    user.get_token()
    user.token_expires = now - datetime.timedelta(seconds=1)
    session.add(user)
    session.commit()

    assert get_user_from_token(session, user.token) is None

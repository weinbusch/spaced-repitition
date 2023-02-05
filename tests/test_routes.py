import contextlib
import datetime

from flask import url_for, template_rendered, current_app

from juliano.domain import Item
from juliano.auth import User

now = datetime.datetime.utcnow()


# Helpers


@contextlib.contextmanager
def templates_used(app):
    templates = []

    def record(sender, template, context, **extra):
        templates.append(template.name)

    template_rendered.connect(record, app)
    yield templates
    template_rendered.disconnect(record, app)


# Index view


def test_index_redirects_anonymous_user(flask_anonymous_client):
    response = flask_anonymous_client.get(url_for("index"))
    assert response.status_code == 302


def test_index_view_for_fresh_user(flask_client):
    response = flask_client.get(url_for("index"))
    assert response.status_code == 200


def test_index_view_create_item(flask_client, session):
    response = flask_client.post(url_for("index"), data={"word": "foo"})
    assert response.status_code == 302
    assert session.query(Item).filter_by(word="foo").count() == 1


def test_cannot_create_duplicate_words(flask_client, session):
    response = flask_client.post(url_for("index"), data={"word": "foo"})
    assert response.status_code == 302
    response = flask_client.post(url_for("index"), data={"word": "foo"})
    assert response.status_code == 200
    assert session.query(Item).filter_by(word="foo").count() == 1


# List view


def test_items_list_view(superuser, flask_client, session):
    session.add(Item(user=superuser, word="foobarbaz"))
    session.commit()
    response = flask_client.get(url_for("item_list"))
    assert response.status_code == 200
    assert b"foobarbaz" in response.data


# Train view


def test_train_dispatch_view_redirects(superuser, flask_client, session):
    item = Item(user=superuser, word="foo", next_iteration=now)
    session.add(item)
    session.commit()

    response = flask_client.get(url_for("train"))

    assert response.status_code == 302
    assert response.location.endswith(url_for("train_item", id=item.id))


def test_train_dispatch_view_if_no_items_left(flask_app, flask_client, session):
    with templates_used(flask_app) as templates:
        response = flask_client.get(url_for("train"))

    assert response.status_code == 200
    assert "training_complete.html" in templates


def test_train_item(superuser, flask_app, flask_client, session):
    item = Item(user=superuser, word="foo", next_iteration=now)
    session.add(item)
    session.commit()

    with templates_used(flask_app) as templates:
        response = flask_client.get(url_for("train_item", id=item.id))

    assert response.status_code == 200
    assert "train_item.html" in templates


def test_train_item_not_found(flask_client):
    response = flask_client.get(url_for("train_item", id=1))
    assert response.status_code == 404


def test_train_item_post_request(superuser, flask_client, session):
    item = Item(user=superuser, word="foo", next_iteration=now)
    session.add(item)
    session.commit()

    data = {"grade": "5"}
    response = flask_client.post(url_for("train_item", id=item.id), data=data)
    session.refresh(item)

    assert response.status_code == 302
    assert item.events[0].grade == 5


def test_train_item_redirects_to_next_item(superuser, flask_client, session):
    for word in ["foo", "bar"]:
        item = Item(user=superuser, word=word, next_iteration=now)
        session.add(item)
    session.commit()

    data = {"grade": 5}
    response = flask_client.post(url_for("train_item", id=1), data=data)

    assert response.status_code == 302
    assert response.location.endswith(url_for("train_item", id=2))


def test_train_last_item_redirects_to_dispatcher(superuser, flask_client, session):
    item = Item(user=superuser, word="foo", next_iteration=now)
    session.add(item)
    session.commit()

    data = {"grade": 5}
    response = flask_client.post(url_for("train_item", id=1), data=data)

    assert response.status_code == 302
    assert response.location.endswith(url_for("train"))


def test_train_item_returns_error_if_item_is_no_longer_due(
    superuser, flask_app, flask_client, session
):
    item = Item(user=superuser, word="foo", next_iteration=now)
    item.train(5)
    session.add(item)
    session.commit()

    data = {"grade": 5}
    with templates_used(flask_app) as templates:
        response = flask_client.post(url_for("train_item", id=1), data=data)

    assert response.status_code == 200
    assert "train_error.html" in templates


# Activate API view


def test_item_activate(superuser, flask_token_client, session):
    item = Item(id=1, user=superuser, word="foo")
    session.add(item)
    session.commit()

    response = flask_token_client.patch(
        url_for("item_activate", item_id=1), json={"is_active": False}
    )

    assert response.status_code == 200
    assert response.json == {"id": 1, "word": "foo", "is_active": False}


def test_item_activate_is_persistent(superuser, flask_token_client, session):
    item = Item(id=1, user=superuser, word="foo")
    session.add(item)
    session.commit()

    flask_token_client.patch(
        url_for("item_activate", item_id=1), json={"is_active": False}
    )

    assert item.is_active is False


def test_item_activate_wrong_item_id(flask_token_client):
    response = flask_token_client.patch(
        url_for("item_activate", item_id=1), json={"is_active": False}
    )
    assert response.status_code == 404


def test_item_activate_reject_anonymous_user(
    superuser, flask_anonymous_client, session
):
    session.add(Item(id=1, user=superuser))
    session.commit()
    response = flask_anonymous_client.patch(
        url_for("item_activate", item_id=1), json={"is_active": False}
    )
    assert response.status_code == 401


def test_item_activate_reject_unauthorized_user(flask_token_client, session):
    other_user = User()
    session.add(Item(id=1, user=other_user))
    session.commit()
    response = flask_token_client.patch(
        url_for("item_activate", item_id=1), json={"is_active": False}
    )
    assert response.status_code == 403


# Settings view


def test_user_settings(flask_client):
    response = flask_client.get(url_for("settings"))
    assert response.status_code == 200


def test_change_user_settings(flask_client, superuser, session):
    assert superuser.settings.max_todo == 10
    assert superuser.settings.max_trainings == 4
    response = flask_client.post(
        url_for("settings"),
        data={
            "max_todo": "20",
            "max_trainings": "10",
        },
    )
    assert response.status_code == 302
    session.refresh(superuser)
    assert superuser.settings.max_todo == 20
    assert superuser.settings.max_trainings == 10


# Auth views


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

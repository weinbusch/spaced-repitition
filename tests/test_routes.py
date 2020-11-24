import datetime

from flask import url_for

from juliano.models import Item, User


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


def test_create_item_with_very_long_word(flask_client, session):
    response = flask_client.post(
        url_for("index"), data={"word": "a very long word" * 1000}
    )
    assert response.status_code == 200


def test_train_view_shows_next_item(flask_client, session):
    session.add(Item(user_id=1, word="foobarbaz"))
    session.commit()
    response = flask_client.get(url_for("train"))
    assert response.status_code == 200
    assert b"foobarbaz" in response.data


def test_train_view_post_grade_increments_repitition_number(flask_client, session):
    item = Item(user_id=1, word="foo", repitition_number=0)
    session.add(item)
    session.commit()
    response = flask_client.post(url_for("train"), data={"grade": "5"})
    session.refresh(item)
    assert response.status_code == 302
    assert item.repitition_number == 1


def test_train_view_cycles_through_pending_items(flask_client, session):
    url = url_for("train")
    now = datetime.datetime.utcnow()

    session.add_all(
        [
            Item(
                user_id=1,
                word="barbazfoo",
                next_iteration=now - datetime.timedelta(days=2),
            ),
            Item(
                user_id=1,
                word="bazfoobar",
                next_iteration=now - datetime.timedelta(days=1),
            ),
            User(id=2),
            Item(
                user_id=2,  # this item should be skipped!
                word="foobarbaz",
                next_iteration=now - datetime.timedelta(days=3),
            ),
        ]
    )
    session.commit()

    response = flask_client.get(url)
    assert b"barbazfoo" in response.data
    assert b"foobarbaz" not in response.data

    response = flask_client.post(url, data={"grade": "5"})
    assert response.status_code == 302

    response = flask_client.get(url)
    assert b"bazfoobar" in response.data
    assert b"foobarbaz" not in response.data

    response = flask_client.post(url, data={"grade": "5"})
    assert response.status_code == 302

    response = flask_client.get(url)
    assert b"foobarbaz" not in response.data


def test_train_view_if_no_items_are_pending(flask_client):
    url = url_for("train")

    response = flask_client.get(url)
    assert response.status_code == 200

    response = flask_client.post(url, data={"grade": "5"})
    assert response.status_code == 200

import pytest
import datetime

from sqlalchemy.exc import IntegrityError

from juliano.repo import Repository
from juliano.domain import Item
from juliano.auth import User

now = datetime.datetime.utcnow()


def create_user(session, username):
    """Create User and saves it to the db

    Only needed in this test. Does not override
    `juliano.auth.create_user'.

    """
    user = User(username)
    session.add(user)
    session.commit()
    return user


def test_create_user(session):
    user = create_user(session, "foo")
    assert user.id == 1


def test_item_roundtrip(session):
    foo = create_user(session, "foo")
    bar = create_user(session, "bar")

    repo = Repository(session)

    repo.add(Item(word="foo", user=foo))
    repo.add(Item(word="bar", user=bar))

    session.commit()

    item = repo.get(1)
    item.train(5)

    session.commit()

    item = repo.get(1)

    assert item.user.username == "foo"

    assert item.word == "foo"
    assert item.is_active is True
    assert item.created - now < datetime.timedelta(seconds=5)
    assert item.easiness_factor > 2.5
    assert item.inter_repitition_interval == datetime.timedelta(days=1)
    assert item.next_iteration > now

    assert item.events[0].created - now < datetime.timedelta(seconds=5)
    assert item.events[0].grade == 5


def test_get_items_for_user(session):
    foo = create_user(session, "foo")
    bar = create_user(session, "bar")
    repo = Repository(session)
    words = {"foo", "bar", "baz"}
    for word in words:
        repo.add(Item(word=word, user=foo))
    repo.add(Item(word="foobar", user=bar))
    session.commit()

    assert {item.word for item in repo.list(user=foo)} == words
    assert {item.word for item in repo.list(user=bar)} == {"foobar"}


def test_items_are_unique_for_word_and_user(session):
    repo = Repository(session)
    foo = create_user(session, "foo")
    bar = create_user(session, "bar")

    repo.add(Item(word="foo", user=foo))
    repo.add(Item(word="foo", user=bar))

    session.commit()

    repo.add(Item(word="bar", user=foo))

    session.commit()

    repo.add(Item(word="foo", user=foo))

    with pytest.raises(IntegrityError):
        session.commit()


def test_items_sorted_by_due_date(session):
    repo = Repository(session)
    foo = create_user(session, "foo")
    for id, d in enumerate([7, 2, 1, 9, 4, 6, 3, 8, 5]):
        repo.add(
            Item(
                id=id,
                user=foo,
                word=f"{id}",
                next_iteration=now + datetime.timedelta(days=d),
            )
        )
        session.commit()
    items = repo.list(user=foo)
    assert [item.next_iteration for item in items] == [
        now + datetime.timedelta(days=d) for d in [1, 2, 3, 4, 5, 6, 7, 8, 9]
    ]

import pytest
import datetime
import contextlib

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from juliano.repo import ItemRepository, UserRepository
from juliano.domain import Item
from juliano.auth import User

now = datetime.datetime.utcnow()


@contextlib.contextmanager
def count_sql_statements(engine):
    stmts = []

    def count(**kwargs):
        s = kwargs.get("statement", None)
        if s:
            stmts.append(s)

    event.listen(engine, "before_cursor_execute", count, named=True)
    yield stmts
    event.remove(engine, "before_cursor_execute", count)


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
    repo = ItemRepository(session)

    foo = create_user(session, "foo")
    item = Item(word="foo", user=foo)
    item.train(5)

    repo.add(item)
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
    repo = ItemRepository(session)
    words = {"foo", "bar", "baz"}
    for word in words:
        repo.add(Item(word=word, user=foo))
    repo.add(Item(word="foobar", user=bar))
    session.commit()

    assert {item.word for item in repo.list(user=foo)} == words
    assert {item.word for item in repo.list(user=bar)} == {"foobar"}


def test_items_are_unique_for_word_and_user(session):
    repo = ItemRepository(session)
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
    repo = ItemRepository(session)
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


def test_repo_issues_one_select_statement(engine, session):
    repo = ItemRepository(session)
    user = User(username="foo")
    for word in ["foo", "bar", "baz"]:
        item = Item(word=word, user=user)
        item.train(5)
        repo.add(item)
    session.commit()

    assert user.username == "foo"
    # otherwise, repo.list(user) issues a select statement targeting
    # the users table

    with count_sql_statements(engine) as stmts:
        items = repo.list(user=user)
        assert all(item.events for item in items)
        assert len(stmts) == 1


def test_user_repository_create_user(session):
    repo = UserRepository(session)
    repo.create_user(username="foo", password="1234")
    session.commit()

    assert repo.get(1).username == "foo"


def test_user_repository_get_user_by_token(session):
    repo = UserRepository(session)
    user = User()
    token = user.get_token()
    repo.add(user)
    session.commit()

    user = repo.get_from_token("wrong-token")
    assert user is None

    user = repo.get_from_token(token)
    assert user is not None
    user.token_expires = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    repo.add(user)
    session.commit()

    user = repo.get_from_token(token)
    assert user is None


def test_user_repository_settings(session):
    repo = UserRepository(session)
    repo.create_user(username="foo", password="1234")
    session.commit()

    user = repo.get(1)
    user.settings.max_todo = 20
    repo.add(user)
    session.commit()

    assert repo.get(1).settings.max_todo == 20


def test_user_repository_default_settings(session):
    repo = UserRepository(session)
    repo.create_user(username="foo", password="1234")
    session.commit()

    assert repo.get(1).settings is not None
    assert repo.get(1).settings.max_todo == 10

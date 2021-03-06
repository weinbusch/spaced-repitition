import datetime

from juliano.models import Item, User
from juliano.spaced_repitition import get_items_for_user, update_item


def test_get_items_for_user(session):
    u1 = User(id=1)
    u2 = User(id=2)
    session.add_all(
        [
            u1,
            u2,
            Item(id=1, user=u1),
            Item(id=2, user=u2),
        ]
    )
    items = get_items_for_user(session, u1).all()
    assert len(items) == 1 and items[0].id == 1


def test_get_items_sorted_by_due_date(session):
    user = User(id=1)
    session.add_all(
        [
            user,
            Item(
                id=1,
                user=user,
                next_iteration=datetime.datetime.utcnow() + datetime.timedelta(days=10),
            ),
            Item(
                id=2,
                user=user,
                next_iteration=datetime.datetime.utcnow() + datetime.timedelta(days=1),
            ),
        ]
    )
    items = get_items_for_user(session, user).all()
    assert [x.id for x in items] == [2, 1]


def test_exclude_inactive_items(session):
    user = User(id=1)
    session.add_all(
        [
            user,
            Item(id=1, user=user),
            Item(id=2, user=user, next_iteration=datetime.datetime.utcnow()),
            Item(
                id=3,
                user=user,
                next_iteration=datetime.datetime.utcnow(),
                is_active=False,
            ),
        ]
    )
    items = get_items_for_user(session, user).all()
    assert len(items) == 2


def test_include_inactive_items(session):
    user = User(id=1)
    session.add_all(
        [
            user,
            Item(id=1, user=user),
            Item(id=2, user=user, next_iteration=datetime.datetime.utcnow()),
            Item(
                id=3,
                user=user,
                next_iteration=datetime.datetime.utcnow(),
                is_active=False,
            ),
        ]
    )
    items = get_items_for_user(session, user, include_inactive=True).all()
    assert len(items) == 3


def test_get_todo_items(session):
    user = User(id=1)
    session.add_all(
        [
            user,
            Item(id=1, user=user, next_iteration=None),
            Item(
                id=2,
                user=user,
                next_iteration=datetime.datetime.utcnow()
                - datetime.timedelta(seconds=1),
            ),
            Item(
                id=3,
                user=user,
                next_iteration=datetime.datetime.utcnow() + datetime.timedelta(days=1),
            ),
        ]
    )
    items = get_items_for_user(session, user, todo=True).all()
    assert [x.id for x in items] == [1, 2]


def test_exclude_inactive_items_from_todo_list(session):
    user = User(id=1)
    session.add_all(
        [
            user,
            Item(id=1, user=user),
            Item(id=2, user=user, next_iteration=datetime.datetime.utcnow()),
            Item(
                id=3,
                user=user,
                next_iteration=datetime.datetime.utcnow(),
                is_active=False,
            ),
        ]
    )
    todo_items = get_items_for_user(session, user, todo=True).all()
    assert len(todo_items) == 2


def test_update_item_sets_last_learned_timestamp(session):
    item = Item(id=1)
    session.add(item)
    session.commit()
    item = update_item(session, item, grade=1)
    assert abs(item.last_learned - datetime.datetime.utcnow()) <= datetime.timedelta(
        seconds=1
    )
    # assert item.last_learned == datetime.datetime.utcnow()


def test_update_item_adds_event(session):
    item = Item(id=1)
    session.add(item)
    session.commit()

    item = update_item(session, item, grade=1)
    assert item.events[0].grade == 1


def test_update_item_sets_next_iteration_datetime(session):
    now = datetime.datetime.utcnow()

    item = Item(id=1)
    session.add(item)
    session.commit()

    item = update_item(session, item, grade=1)

    assert item.next_iteration > now

import datetime

from juliano.models import Item, User, Event
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
    items = get_items_for_user(session, u1)
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
    items = get_items_for_user(session, user)
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
    items = get_items_for_user(session, user)
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
    items = get_items_for_user(session, user, include_inactive=True)
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
    items = get_items_for_user(session, user, todo=True)
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
    todo_items = get_items_for_user(session, user, todo=True)
    assert len(todo_items) == 2


def test_limit_number_of_todo_items(session):
    user = User(id=1)
    now = datetime.datetime.utcnow()
    items = [Item(user=user, id=pk, next_iteration=now) for pk in range(100)]
    session.add_all(items)
    todo_items = get_items_for_user(session, user, todo=True, maximum_todo=10)
    assert len(todo_items) == 10


def test_maximum_number_of_calculated_based_on_events(session):
    user = User(id=1)
    now = datetime.datetime.utcnow()
    today = datetime.date.today()
    items = [Item(user=user, id=pk, next_iteration=now) for pk in range(100)]
    session.add_all(items)
    session.add(Event(id=1, item_id=1, grade=1, created=now))
    session.commit()
    item = session.query(Item).get(1)
    todo_items = get_items_for_user(session, user, todo=True, maximum_todo=10)
    assert len(todo_items) == 9


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

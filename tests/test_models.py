import pytest
import datetime

from sqlalchemy.exc import IntegrityError

from juliano.models import Item, User, Event


now = datetime.datetime.utcnow()


def test_items_are_unique_for_word_and_user(session):
    u1 = User(id=1)
    u2 = User(id=2)
    i1 = Item(user=u1, word="foo")
    i2 = Item(user=u2, word="foo")
    session.add_all([u1, u2, i1, i2])
    session.commit()  # should not raise

    session.add(Item(user=u1, word="foo"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_item_is_active_by_default(session):
    item = Item()
    session.add(item)
    session.commit()
    assert item.is_active is True


def test_item_to_dict():
    item = Item(id=1, word="foo", is_active=True)
    assert item.to_dict() == {
        "id": 1,
        "word": "foo",
        "is_active": True,
    }


def test_event_has_created_datetime(session):
    event = Event(grade=3)
    session.add(event)
    session.commit()
    assert abs(event.created - datetime.datetime.utcnow()) <= datetime.timedelta(
        seconds=1
    )


def test_events_can_be_added_to_items(session):
    item = Item(word="foo")
    session.add(item)
    event = Event(grade=1, created=datetime.datetime.utcnow())
    item.events.append(event)
    assert abs(
        item.events[0].created - datetime.datetime.utcnow()
    ) <= datetime.timedelta(seconds=1)


def test_item_last_trained_calculated_based_on_events(session):
    now = datetime.datetime.utcnow()
    item = Item(word="foo")
    session.add(item)
    item.events.append(Event(grade=1, created=now - datetime.timedelta(days=1)))
    item.events.append(Event(grade=1, created=now))
    item.events.append(Event(grade=1, created=now - datetime.timedelta(days=2)))
    session.commit()
    assert item.last_learned == now


def test_deleting_item_deletes_all_associated_events(session):
    item = Item(word="foo")
    item.events.append(Event(grade=1))
    item.events.append(Event(grade=2))
    session.add(item)
    session.commit()

    assert session.query(Event).count() == 2

    session.delete(item)
    session.commit()

    assert session.query(Event).count() == 0


@pytest.mark.parametrize(
    "date, todo",
    [
        (now, True),
        (now + datetime.timedelta(days=1), False),
        (now - datetime.timedelta(days=1), True),
        (None, True),
    ],
)
def test_item_todo(date, todo):
    item = Item(word="foo", next_iteration=date)
    assert item.todo == todo

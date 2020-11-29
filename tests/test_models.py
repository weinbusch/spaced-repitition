import pytest
import datetime

from sqlalchemy.exc import IntegrityError

from juliano.models import Item, User, Event


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


def test_event_grade_is_not_nullable(session):
    session.add(Event())
    with pytest.raises(IntegrityError):
        session.commit()


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
    assert item.events[0].created == datetime.datetime.utcnow()


@pytest.mark.skip
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

import pytest
import datetime
from juliano.domain import Item, filter_todo_items

now = datetime.datetime.utcnow()


def test_create_item():
    item = Item(word="foo")
    assert item.is_active is True
    assert item.next_iteration > now


def test_item_to_dict():
    item = Item(id=1, word="foo")
    assert item.to_dict() == {
        "id": 1,
        "word": "foo",
        "is_active": True,
    }


def test_create_item_sets_timestamp():
    item = Item(word="foo")
    assert item.created - now < datetime.timedelta(seconds=5)


def test_item_add_event():
    item = Item(word="foo")
    item.add_event(grade=3, created=now)
    assert item.events[0].grade == 3
    assert item.events[0].created == now


def test_item_last_learned_is_None():
    item = Item(word="foo")
    assert item.last_learned is None


def test_item_train_sets_last_learned():
    item = Item(word="foo")
    item.train(5)
    assert item.last_learned - now < datetime.timedelta(seconds=5)


def test_item_last_trained_calculated_based_on_events(session):
    item = Item(word="foo")
    for x in range(10):
        item.add_event(grade=1, created=now - datetime.timedelta(days=(x - 5) ** 2))
    assert item.last_learned == now


def test_item_train_creates_event():
    item = Item(word="foo")
    item.train(5)
    event = item.events[0]
    assert event.grade == 5
    assert event.created - now < datetime.timedelta(seconds=5)


def test_item_train_sets_next_iteration():
    item = Item(word="foo")
    item.next_iteration = now
    item.train(5)
    assert item.next_iteration > now


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
    item = Item(word="foo")
    item.next_iteration = date
    assert item.todo == todo


def test_inactive_items_are_not_marked_as_todo():
    item = Item(word="foo")
    item.next_iteration = now
    assert item.todo is True

    item.is_active = False
    assert item.todo is False


def test_filter_todo_items():
    items = [Item(word="todo", next_iteration=now) for _ in range(10)] + [
        Item(word="not_todo", next_iteration=now + datetime.timedelta(days=1))
        for _ in range(10)
    ]
    todo_items = filter_todo_items(items)
    assert len(todo_items) == 10
    assert all(item.word == "todo" for item in todo_items)


def test_filter_todo_items_max_number():
    items = [Item(word="todo", next_iteration=now) for _ in range(20)]
    todo_items = filter_todo_items(items, n=10)
    assert len(todo_items) == 10


def test_filter_todo_items_max_number_takes_events_into_account():
    items = [Item(word="todo", next_iteration=now) for _ in range(20)]
    items[0].train(5)
    # one item was trained today, so we should only return 9 todo
    # items
    todo_items = filter_todo_items(items, n=10)
    assert len(todo_items) == 9

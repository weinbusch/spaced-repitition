import datetime
from juliano.models import Item
from juliano.spaced_repitition import get_word_calendar, get_weekly_word_calendar


def test_word_calendar_is_a_list_of_dates_and_counts():
    now = datetime.datetime.utcnow()
    monday = now - datetime.timedelta(now.weekday())
    items = [Item(created=monday) for _ in range(3)]
    cal = get_word_calendar(items)
    assert cal[0] == (monday.date(), 3)


def test_word_calendar_starts_on_a_monday():
    now = datetime.datetime.utcnow()
    tuesday = now + datetime.timedelta(days=1 - now.weekday())
    monday = tuesday.date() - datetime.timedelta(days=1)
    items = [Item(created=tuesday)]
    cal = get_word_calendar(items)
    assert cal[0] == (monday, 0)


def test_word_calendar_ends_on_a_sunday():
    now = datetime.datetime.utcnow()
    monday = now - datetime.timedelta(days=now.weekday())
    sunday = monday.date() + datetime.timedelta(days=6)
    items = [Item(created=monday)]
    cal = get_word_calendar(items)
    assert cal[-1] == (sunday, 0)


def test_word_calendar_with_empty_list_of_items():
    cal = get_word_calendar([])
    assert cal == []


def test_word_calendar_weeks_returns_list_of_weeks():
    now = datetime.datetime.utcnow()
    items = [
        Item(created=now),
        Item(created=now - datetime.timedelta(days=7)),
    ]
    cal = get_weekly_word_calendar(items)
    assert len(cal) == 2
    assert len(cal[0]) == 7

import datetime
from juliano.models import Item
from juliano.spaced_repitition import get_word_calendar, get_weekly_word_calendar


def test_word_calender_returns_calendar_maximum_value():
    now = datetime.datetime.utcnow()
    monday = now - datetime.timedelta(now.weekday())
    items = [Item(created=monday) for _ in range(3)]
    _, maximum = get_word_calendar(items)
    assert maximum == 3


def test_word_calendar_is_a_list_of_dates_and_counts():
    now = datetime.datetime.utcnow()
    monday = now - datetime.timedelta(now.weekday())
    items = [Item(created=monday) for _ in range(3)]
    cal, _ = get_word_calendar(items)
    assert cal[-7] == (monday.date(), 3)


def test_word_calendar_starts_on_a_monday():
    now = datetime.datetime.utcnow()
    tuesday = now + datetime.timedelta(days=1 - now.weekday())
    items = [Item(created=tuesday)]
    cal, _ = get_word_calendar(items)
    assert cal[0][0].weekday() == 0


def test_word_calendar_ends_on_a_sunday():
    now = datetime.datetime.utcnow()
    monday = now - datetime.timedelta(days=now.weekday())
    sunday = monday.date() + datetime.timedelta(days=6)
    items = [Item(created=monday)]
    cal, _ = get_word_calendar(items)
    assert cal[-1] == (sunday, 0)


def test_word_calendar_covers_12_weeks():
    now = datetime.datetime.utcnow()
    items = [Item(created=now)]
    cal, _ = get_word_calendar(items)
    assert len(cal) == 7 * 12


def test_word_calendar_with_empty_list_of_items():
    cal, maximum = get_word_calendar([])
    assert cal == []
    assert maximum is None


def test_word_calendar_weeks_returns_list_of_weeks():
    now = datetime.datetime.utcnow()
    items = [
        Item(created=now),
        Item(created=now - datetime.timedelta(days=7)),
    ]
    cal, maximum = get_weekly_word_calendar(items)
    assert len(cal) == 12
    assert len(cal[0]) == 7

import datetime
from juliano.models import Item
from juliano.spaced_repitition import get_word_calendar


def test_word_calendar_is_a_list_of_dates_and_counts():
    now = datetime.datetime.utcnow()
    today = now.date()
    yesterday = today - datetime.timedelta(days=1)
    items = [Item(created=now - datetime.timedelta(days=x)) for x in [0, 1, 1]]
    cal = get_word_calendar(items)
    assert cal[-1] == (today, 1)
    assert cal[-2] == (yesterday, 2)


def test_word_calendar_starts_on_a_monday():
    now = datetime.datetime.utcnow()
    tuesday = now + datetime.timedelta(days=1 - now.weekday())
    monday = tuesday.date() - datetime.timedelta(days=1)
    items = [Item(created=tuesday)]
    cal = get_word_calendar(items)
    assert cal[0] == (monday, 0)

import datetime
from juliano.models import Item
from juliano.spaced_repitition import get_histogram


def test_histogram_is_list_of_dates_and_counts():
    now = datetime.datetime.utcnow()
    today = now.date()
    days = [1, 1, 3, 3, 3]
    items = [Item(created=now - datetime.timedelta(days=x)) for x in days]
    histogram = get_histogram(items)
    assert histogram[0] == (today, 0)
    assert histogram[1] == (today - datetime.timedelta(days=1), 2)
    assert histogram[2] == (today - datetime.timedelta(days=2), 0)
    assert histogram[3] == (today - datetime.timedelta(days=3), 3)

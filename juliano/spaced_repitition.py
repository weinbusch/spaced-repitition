import itertools
import collections
import datetime

from sqlalchemy import or_
from .models import Item, Event


def get_items_for_user(db_session, user, todo=False, include_inactive=False):
    query = db_session.query(Item).filter(Item.user == user)

    if not include_inactive:
        query = query.filter(Item.is_active.is_(True))

    if todo:
        query = query.filter(
            or_(
                Item.next_iteration <= datetime.datetime.utcnow(),
                Item.next_iteration.is_(None),
            )
        )

    query = query.order_by(Item.next_iteration)

    return query


def update_item(db_session, item, grade):
    """Spaced repition algorithm

    https://en.wikipedia.org/wiki/SuperMemo#Description_of_SM-2_algorithm
    """

    now = datetime.datetime.utcnow()
    event = Event(grade=grade, created=now)

    item.events.append(event)

    if item.repitition_number < 3:
        item.inter_repitition_interval = datetime.timedelta(days=1)
    else:
        item.inter_repitition_interval = (
            item.inter_repitition_interval * item.easiness_factor
        )

    increment = dict(
        [
            (0, -0.8),
            (1, -0.54),
            (2, -0.32),
            (3, -0.14),
            (4, 0),
            (5, 0.1),
        ]
    )

    item.easiness_factor += increment[grade]

    if item.easiness_factor < 1.3:
        item.easiness_factor = 1.3

    item.next_iteration = event.created + item.inter_repitition_interval

    return item


def date_range(start, end):
    days = (end - start).days
    return (start + datetime.timedelta(days=x) for x in range(days))


def get_word_calendar(items):

    today = datetime.date.today()
    next_monday = today + datetime.timedelta(days=7 - today.weekday())
    first_monday = next_monday - datetime.timedelta(days=12 * 7)

    dates = (
        item.created.date() for item in items if item.created.date() >= first_monday
    )
    counts = collections.Counter(dates)
    maximum = max(counts.values(), default=0)

    return (
        [(date, counts[date]) for date in date_range(first_monday, next_monday)],
        maximum,
    )


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks

    From the itertools documentation
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def get_weekly_word_calendar(items):
    cal, maximum = get_word_calendar(items)
    return (list(grouper(cal, 7)), maximum)

import itertools
import collections
import datetime


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

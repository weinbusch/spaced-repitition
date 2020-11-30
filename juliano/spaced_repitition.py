import datetime

from sqlalchemy import or_
from .models import Item, Event


def get_items_for_user(db_session, user, todo=False):
    query = db_session.query(Item).filter(Item.user == user)

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

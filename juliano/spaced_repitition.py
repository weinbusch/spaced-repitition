import datetime

from sqlalchemy import or_
from .models import Item


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


def update_item(item, grade):
    """Spaced repition algorithm

    https://en.wikipedia.org/wiki/SuperMemo#Description_of_SM-2_algorithm
    """
    if item.repitition_number == 0:
        item.inter_repitition_interval = datetime.timedelta(days=1)
    elif item.repitition_number == 1:
        item.inter_repitition_interval = datetime.timedelta(
            days=1
        )  # deviating from SM-2
    else:
        item.inter_repitition_interval = (
            item.inter_repitition_interval * item.easiness_factor
        )
    item.easiness_factor = item.easiness_factor + (
        0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)
    )
    if item.easiness_factor < 1.3:
        item.easiness_factor = 1.3

    item.repitition_number += 1

    item.last_learned = datetime.datetime.utcnow()

    item.next_iteration = item.last_learned + item.inter_repitition_interval

    return item

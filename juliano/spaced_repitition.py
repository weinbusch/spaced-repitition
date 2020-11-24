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


def update_word(word, grade):
    """Spaced repition algorithm

    https://en.wikipedia.org/wiki/SuperMemo#Description_of_SM-2_algorithm
    """
    if word.repitition_number == 0:
        word.inter_repitition_interval = datetime.timedelta(days=1)
    elif word.repitition_number == 1:
        word.inter_repitition_interval = datetime.timedelta(
            days=1
        )  # deviating from SM-2
    else:
        word.inter_repitition_interval = (
            word.inter_repitition_interval * word.easiness_factor
        )
    word.easiness_factor = word.easiness_factor + (
        0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)
    )
    if word.easiness_factor < 1.3:
        word.easiness_factor = 1.3

    word.repitition_number += 1

    word.last_learned = datetime.datetime.utcnow()

    word.next_iteration = word.last_learned + word.inter_repitition_interval

    return word

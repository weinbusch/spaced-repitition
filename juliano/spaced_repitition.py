import datetime

from .models import Item


def get_next_word(db_session, current_user):
    return (
        db_session.query(Item)
        .filter_by(user=current_user)
        .order_by(Item.last_learned)
        .first()
    )


def update_word(word, grade):
    word.repitition_number += 1
    word.last_learned = datetime.datetime.utcnow()
    return word

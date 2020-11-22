from .models import Item


def get_next_word(db_session, current_user):
    return db_session.query(Item).filter_by(user=current_user).first()


def update_word(word, grade):
    word.repitition_number += 1
    return word

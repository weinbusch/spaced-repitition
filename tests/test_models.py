import pytest

from sqlalchemy.exc import IntegrityError

from juliano.models import Item, User


def test_items_are_unique_for_word_and_user(session):
    u1 = User(id=1)
    u2 = User(id=2)
    i1 = Item(user=u1, word="foo")
    i2 = Item(user=u2, word="foo")
    session.add_all([u1, u2, i1, i2])
    session.commit()  # should not raise

    session.add(Item(user=u1, word="foo"))
    with pytest.raises(IntegrityError):
        session.commit()

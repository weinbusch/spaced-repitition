import datetime

from juliano.auth import User


def test_verify_password():
    user = User.create_user(username="foo", password="1234")
    assert user.verify_password("1234") is True
    assert user.verify_password("123$") is False


def test_get_token():
    user = User()
    user.get_token()
    assert user.token is not None
    assert user.token_expires is not None


def test_check_if_token_is_expired():
    now = datetime.datetime.utcnow()
    user = User()
    user.get_token()
    assert user.token_is_expired() is False

    user.token_expires = now - datetime.timedelta(seconds=1)
    assert user.token_is_expired() is True


def test_get_expired_token():
    now = datetime.datetime.utcnow()
    user = User()
    t1 = user.get_token()
    user.token_expires = now - datetime.timedelta(seconds=1)
    t2 = user.get_token()
    assert t1 != t2
    assert t2 == user.token


def test_user_settings():
    user = User(username="foo")
    assert user.settings.max_todo == 10

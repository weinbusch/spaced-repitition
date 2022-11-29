import datetime
import secrets

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


class Settings:
    def __init__(self):
        self.max_todo = 10


class User(UserMixin):
    def __init__(self, username=None, password_hash=None):
        self.id = None
        self.username = username
        self.password_hash = password_hash
        self.token = None
        self.token_expires = None
        self.settings = Settings()

    def get_token(self):
        now = datetime.datetime.utcnow()
        if self.token_is_expired():
            self.token = secrets.token_hex(32)
            self.token_expires = now + datetime.timedelta(seconds=60 * 60 * 24)
        return self.token

    def token_is_expired(self):
        now = datetime.datetime.utcnow()
        return not self.token or self.token_expires is None or self.token_expires < now

    def verify_password(self, password):
        return _verify_password(self.password_hash, password)

    @classmethod
    def create_user(cls, username, password):
        password_hash = _create_password_hash(password)
        return cls(username=username, password_hash=password_hash)


def _validate_password(password):
    if len(password) > 64:
        raise ValueError(
            "Das Passwort ist zu lang (Kannst Du Dir das wirklich merken?)"
        )


def _create_password_hash(password):
    _validate_password(password)
    return generate_password_hash(password, salt_length=16)


def _verify_password(hash, password):
    try:
        _validate_password(password)
    except ValueError:
        return False
    return check_password_hash(hash, password)

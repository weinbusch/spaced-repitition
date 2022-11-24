import datetime
import secrets

from functools import wraps

from flask import abort

from flask_login import LoginManager, current_user, UserMixin


from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo, ValidationError, Length
from werkzeug.security import generate_password_hash, check_password_hash

from .app import db_session


class User(UserMixin):
    def __init__(self, username=None, password_hash=None, id=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.token = None

    def get_token(self):
        now = datetime.datetime.utcnow()
        if not self.token or self.token_expires < now:
            self.token = secrets.token_hex(32)
            self.token_expires = now + datetime.timedelta(seconds=60 * 60 * 24)
        return self.token


class TokenLoginManager(LoginManager):
    def init_app(self, app, *args, **kwargs):
        super().init_app(app, *args, **kwargs)

        @app.before_request
        def set_current_user_token():
            if current_user.is_authenticated:
                current_user.get_token()
                db_session.add(current_user)
                db_session.commit()


login_manager = TokenLoginManager()
login_manager.login_view = "login"


@login_manager.user_loader
def user_loader(id):
    return get_user(db_session, id)


@login_manager.request_loader
def load_user_from_request(request):
    data = request.headers.get("Authorization", "")
    if data.startswith("Bearer "):
        _, token = data.split("Bearer ", maxsplit=1)
        return get_user_from_token(db_session, token)
    return None


class LoginForm(Form):

    username = StringField(
        "Benutzername",
        validators=[
            InputRequired(),
            Length(max=64, message="Dieser Name ist zu lang."),
        ],
    )
    password = PasswordField(
        "Passwort",
        validators=[
            InputRequired(),
            Length(
                max=64,
                message="Das Passwort ist zu lang (Kannst Du Dir das wirklich merken?)",
            ),
        ],
    )


def validate_unique_username(form, field):
    if db_session.query(User).filter_by(username=field.data).count():
        raise ValidationError(
            "Bitte wähle einen anderen Benutzernamen. Dieser Name existiert bereits. "
        )


class RegisterForm(Form):

    username = StringField(
        "Benutzername",
        validators=[
            InputRequired(),
            Length(max=64, message="Dieser Name ist zu lang."),
            validate_unique_username,
        ],
    )
    password = PasswordField(
        "Passwort",
        validators=[
            InputRequired(),
            Length(
                max=64,
                message="Das Passwort ist zu lang (Kannst Du Dir das wirklich merken?)",
            ),
        ],
    )
    repeat_password = PasswordField(
        "Passwort wiederholen",
        validators=[
            InputRequired(),
            EqualTo("password", message="Die Passwörter müssen übereinstimmen."),
        ],
    )


def _validate_password(password):
    if len(password) > 64:
        raise ValueError(
            "Das Passwort ist zu lang (Kannst Du Dir das wirklich merken?)"
        )


def create_password_hash(password):
    _validate_password(password)
    return generate_password_hash(password, salt_length=16)


def verify_password(hash, password):
    try:
        _validate_password(password)
    except ValueError:
        return False
    return check_password_hash(hash, password)


def create_user(username, password):
    password_hash = create_password_hash(password)
    return User(username=username, password_hash=password_hash)


def get_user(session, id):
    return session.query(User).get(id)


def get_user_from_token(session, token):
    now = datetime.datetime.utcnow()
    user = session.query(User).filter_by(token=token).one_or_none()
    if user and user.token_expires < now:
        return None
    return user


def get_authenticated_user(session, username, password):
    user = session.query(User).filter_by(username=username).one_or_none()
    if user and verify_password(user.password_hash, password):
        return user
    return None


def token_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        return func(*args, **kwargs)

    return decorated_view

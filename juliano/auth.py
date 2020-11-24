from flask_login import LoginManager
from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo, ValidationError, Length
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from .app import db_session


login_manager = LoginManager()
login_manager.login_view = "login"


@login_manager.user_loader
def user_loader(id):
    from juliano.app import get_db

    return get_user(get_db(), id)


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


def get_authenticated_user(session, username, password):
    user = session.query(User).filter_by(username=username).one_or_none()
    if user and verify_password(user.password_hash, password):
        return user
    return None

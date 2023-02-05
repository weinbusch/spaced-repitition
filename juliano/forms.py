from wtforms import Form, StringField, RadioField, PasswordField, IntegerField
from wtforms.validators import InputRequired, EqualTo, ValidationError, Length


def validate_unique_word(form, field):
    data = field.data.strip().lower()
    items = form.items or []
    try:
        next(item for item in items if item.word.lower() == data)
        raise ValidationError("Dieses Wort ist bereits in Deiner Sammlung.")
    except StopIteration:
        pass


class ItemForm(Form):
    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop("items", [])
        super().__init__(*args, **kwargs)

    word = StringField(
        validators=[
            InputRequired(),
            Length(max=1024, message="Dieses Wort ist zu lang."),
            validate_unique_word,
        ],
        filters=[lambda x: x.strip()],
    )


class TrainForm(Form):

    grade = RadioField(
        choices=range(6),
        coerce=int,
        validators=[InputRequired(message="Bitte triff eine Auswahl.")],
    )


validate_password_length = Length(
    max=64,
    message="Das Passwort ist zu lang (Kannst Du Dir das wirklich merken?)",
)


class LoginForm(Form):

    username = StringField(
        "Benutzername",
        validators=[
            InputRequired(),
            Length(max=64, message="Dieser Name ist zu lang."),
        ],
    )
    password = PasswordField(
        "Passwort", validators=[InputRequired(), validate_password_length]
    )


def validate_unique_username(form, field):
    users = form.users or []
    try:
        next(user for user in users if user.username == field.data)
        raise ValidationError(
            "Bitte wähle einen anderen Benutzernamen. Dieser Name existiert bereits. "
        )
    except StopIteration:
        pass


class RegisterForm(Form):
    def __init__(self, *args, **kwargs):
        self.users = kwargs.pop("users", [])
        super().__init__(*args, **kwargs)

    username = StringField(
        "Benutzername",
        validators=[
            InputRequired(),
            Length(max=64, message="Dieser Name ist zu lang."),
            validate_unique_username,
        ],
    )
    password = PasswordField(
        "Passwort", validators=[InputRequired(), validate_password_length]
    )
    repeat_password = PasswordField(
        "Passwort wiederholen",
        validators=[
            InputRequired(),
            EqualTo("password", message="Die Passwörter müssen übereinstimmen."),
        ],
    )


class SettingsForm(Form):

    max_todo = IntegerField(
        "Maximale Anzahl von Übungen pro Tag", validators=[InputRequired()]
    )

    max_trainings = IntegerField("Maximale Anzahl von Wiederholungen pro Wort")

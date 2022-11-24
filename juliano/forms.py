from wtforms import Form, StringField, RadioField
from wtforms.validators import InputRequired, ValidationError, Length

from flask_login import current_user

from .app import db_session
from .domain import Item


def validate_unique_word(form, field):
    count = (
        db_session.query(Item)
        .filter(Item.word.ilike(field.data), Item.user == current_user)
        .count()
    )
    if count:
        raise ValidationError("Dieses Wort ist bereits in Deiner Sammlung.")


class ItemForm(Form):

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

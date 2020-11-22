from wtforms import Form, StringField, RadioField
from wtforms.validators import InputRequired, ValidationError

from flask_login import current_user

from .app import db_session
from .models import Item


class ItemForm(Form):

    word = StringField(validators=[InputRequired()], filters=[lambda x: x.strip()])

    def validate_word(self, word):
        item = (
            db_session.query(Item)
            .filter(Item.word.ilike(word.data), Item.user == current_user)
            .one_or_none()
        )
        if item is not None:
            raise ValidationError("Dieses Wort ist bereits in Deiner Sammlung.")


class TrainForm(Form):

    grade = RadioField(choices=range(1, 6))

from werkzeug.datastructures import MultiDict

from juliano.forms import ItemForm, RegisterForm, LoginForm
from juliano.domain import Item
from juliano.auth import User


def test_item_form_strip_whitespace():
    data = MultiDict(dict(word="  hello world   "))
    form = ItemForm(data)
    assert form.validate() is True
    assert form.data["word"] == "hello world"


def test_item_form_requires_input():
    data = MultiDict()
    form = ItemForm(data)
    assert form.validate() is False


def test_item_form_validates_uniqueness():
    items = [Item(word=word) for word in ["foo", "bar", "baz"]]
    data = MultiDict(dict(word="foo"))
    form = ItemForm(data, items=items)
    assert form.validate() is False


def item_form_rejects_long_word():
    data = MultiDict(dict(word="f" * 1000))
    form = ItemForm(data)
    assert form.validate() is False


def test_login_form_rejects_long_password():
    data = MultiDict(dict(username="foo", password="1" * 65))
    form = LoginForm(data)
    assert form.validate() is False
    assert form.errors["password"]


def test_register_form():
    data = MultiDict(dict(username="foo", password="1234", repeat_password="1234"))
    form = RegisterForm(data)
    assert form.validate() is True
    assert not form.errors


def test_register_form_requires_matching_repeated_password():
    data = MultiDict(dict(username="foo", password="1234", repeat_password="4321"))
    form = RegisterForm(data)
    assert form.validate() is False
    assert form.errors["repeat_password"]


def test_register_form_requires_unique_username():
    users = [User(username) for username in ["foo", "bar", "baz"]]
    data = MultiDict(dict(username="foo", password="1234", repeat_password="1234"))
    form = RegisterForm(data, users=users)
    assert form.validate() is False
    assert form.errors["username"]


def test_register_form_rejects_long_username():
    data = MultiDict(dict(username="f" * 100, password="1234", repeat_password="1234"))
    form = RegisterForm(data)
    assert form.validate() is False
    assert form.errors["username"]


def test_register_form_rejects_long_password():
    data = MultiDict(dict(username="foo", password="1" * 65, repeat_password="1" * 65))
    form = RegisterForm(data)
    assert form.validate() is False
    assert form.errors["password"]

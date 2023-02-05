import datetime
from functools import wraps

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
    jsonify,
)

from flask_login import login_required, login_user, logout_user, current_user

from juliano.db import db_session
from juliano.domain import Item, filter_todo_items_for_user
from juliano.forms import ItemForm, TrainForm, LoginForm, RegisterForm, SettingsForm
from juliano.calendar import get_weekly_word_calendar
from juliano.images import filenames


def token_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        return func(*args, **kwargs)

    return decorated_view


class Router:
    def __init__(self):
        self.routes = []

    def route(self, rule, **options):
        def decorator(func):
            self.register(rule, func, options)

            @wraps(func)
            def wrapped_function(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapped_function

        return decorator

    def register(self, rule, view_func, options):
        self.routes.append((rule, view_func, options))

    def init_app(self, app):
        for rule, view_func, options in self.routes:
            debug_only = options.pop("debug_only", False)
            if debug_only and not app.config["DEBUG"]:
                continue
            app.add_url_rule(rule, view_func=view_func, **options)


router = Router()


@router.route("/", methods=["GET", "POST"])
@login_required
def index():
    repo = db_session.items
    form = ItemForm(request.form, user=current_user, items=repo.list(current_user))
    if request.method == "POST" and form.validate():
        item = Item(word=form.word.data, user=current_user)
        repo.add(item)
        db_session.commit()
        return redirect(url_for("index"))
    items = repo.list(current_user)
    calendar = get_weekly_word_calendar(items)
    todo_items = filter_todo_items_for_user(items, current_user)
    return render_template(
        "index.html", items=items, form=form, todo_items=todo_items, calendar=calendar
    )


@router.route("/list", methods=["GET"])
@login_required
def item_list():
    repo = db_session.items
    items = repo.list(current_user)
    return render_template("item_list.html", items=items)


@router.route("/item/activate/<item_id>", methods=["PATCH"])
@token_required
def item_activate(item_id):
    repo = db_session.items
    item = repo.get(item_id)
    if item is None:
        return abort(404)
    if current_user != item.user:
        return abort(403)
    if request.json and "is_active" in request.json:
        item.is_active = request.json.get("is_active")
        db_session.commit()
    return jsonify(item.to_dict())


@router.route("/train", methods=["GET"])
@login_required
def train():
    "Train dispatch view"
    repo = db_session.items
    items = repo.list(current_user)
    todo_items = filter_todo_items_for_user(items, current_user)
    if todo_items:
        item = todo_items[0]
        return redirect(url_for("train_item", id=item.id))

    return render_template("training_complete.html")


@router.route("/test/train/complete", methods=["GET"], debug_only=True)
@login_required
def test_training_complete():
    return render_template("training_complete.html")


@router.route("/train/<id>", methods=["GET", "POST"])
def train_item(id):
    item = db_session.items.get(id)
    if not item or item.user != current_user:
        return abort(404)
    if not item.todo:
        return render_template("train_error.html", item=item)
    form = TrainForm(request.form)
    if request.method == "POST" and form.validate():
        item.train(**form.data)
        db_session.commit()
        items = db_session.items.list(current_user)
        if todo_items := filter_todo_items_for_user(items, current_user):
            return redirect(url_for("train_item", id=todo_items[0].id))
        return redirect(url_for("train"))
    items = db_session.items.list(current_user)
    todo_items = filter_todo_items_for_user(items, current_user)
    return render_template(
        "train_item.html", form=form, item=item, remaining=len(todo_items) - 1
    )


@router.route("/test/train/error", methods=["GET"], debug_only=True)
@login_required
def test_training_error():
    item = Item()
    item.train(5)
    item.events[0].created = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    return render_template("train_error.html", item=item)


@router.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm(request.form, obj=current_user.settings)
    if request.method == "POST" and form.validate():
        user_repo = db_session.users
        form.populate_obj(current_user.settings)
        user_repo.add(current_user)
        db_session.commit()
        return redirect(url_for("index"))
    return render_template("settings.html", form=form)


@router.route("/login", methods=["GET", "POST"])
def login():
    repo = db_session.users
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = repo.get_authenticated_user(**form.data)
        if user:
            login_user(user)
            return redirect(url_for("index"))
        flash(
            (
                "Dein Benutzername und Passwort passen nicht zusammen. "
                "Bitte versuche es erneut oder lege ein neues Konto an."
            ),
            "login_error",
        )
    return render_template("login.html", form=form)


@router.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@router.route("/register", methods=["GET", "POST"])
def register():
    if not current_app.config["REGISTER_VIEW"]:
        return abort(404)
    user_repo = db_session.users
    form = RegisterForm(request.form, users=user_repo.list())
    if request.method == "POST" and form.validate():
        user = user_repo.create_user(form.username.data, form.password.data)
        db_session.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html", form=form)


@router.route("/images", methods=["GET"])
@login_required
def all_images():
    if not current_app.config["DEBUG"]:
        abort(404)
    return render_template("images.html", filenames=filenames)

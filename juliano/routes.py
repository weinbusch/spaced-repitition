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

from juliano.app import app, csrf, db_session
from juliano.domain import Item, filter_todo_items
from juliano.forms import ItemForm, TrainForm
from juliano.auth import (
    get_authenticated_user,
    LoginForm,
    create_user,
    RegisterForm,
    token_required,
)
from juliano.repo import Repository
from juliano.calendar import get_weekly_word_calendar
from juliano.images import filenames


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    repo = Repository(db_session)
    form = ItemForm(request.form)
    if request.method == "POST" and form.validate():
        item = Item(word=form.word.data, user=current_user)
        repo.add(item)
        db_session.commit()
        return redirect(url_for("index"))
    items = repo.list(current_user)
    calendar = get_weekly_word_calendar(items)
    todo_items = filter_todo_items(items, n=10)
    return render_template(
        "index.html", items=items, form=form, todo_items=todo_items, calendar=calendar
    )


@app.route("/list", methods=["GET"])
@login_required
def item_list():
    repo = Repository(db_session)
    items = repo.list(current_user)
    return render_template("item_list.html", items=items)


@app.route("/item/activate/<item_id>", methods=["PATCH"])
@csrf.exempt
@token_required
def item_activate(item_id):
    repo = Repository(db_session)
    item = repo.get(item_id)
    if item is None:
        return abort(404)
    if current_user != item.user:
        return abort(403)
    if request.json and "is_active" in request.json:
        item.is_active = request.json.get("is_active")
        db_session.commit()
    return jsonify(item.to_dict())


@app.route("/train", methods=["GET", "POST"])
@login_required
def train():
    repo = Repository(db_session)
    items = repo.list(current_user)
    items = filter_todo_items(items, n=10)
    form = TrainForm(request.form)
    if items and request.method == "POST" and form.validate():
        items[0].train(**form.data)
        db_session.commit()
        return redirect(url_for("train"))
    return render_template("train.html", items=items, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = get_authenticated_user(db_session, **form.data)
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if not current_app.config["REGISTER_VIEW"]:
        return abort(404)
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        user = create_user(form.username.data, form.password.data)
        db_session.add(user)
        db_session.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html", form=form)


@app.route("/images")
@login_required
def all_images():
    if not app.config["DEBUG"]:
        abort(404)
    return render_template("images.html", filenames=filenames)

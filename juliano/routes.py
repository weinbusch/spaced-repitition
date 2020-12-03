from flask import render_template, request, redirect, url_for, flash, abort

from flask_login import login_required, login_user, logout_user, current_user

from .app import app, db_session
from .models import Item
from .forms import ItemForm, TrainForm
from .auth import get_authenticated_user, LoginForm, create_user, RegisterForm
from .spaced_repitition import update_item, get_items_for_user, get_weekly_word_calendar
from .images import filenames


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ItemForm(request.form)
    items = get_items_for_user(db_session, user=current_user).all()
    calendar = get_weekly_word_calendar(items)
    todo_items = get_items_for_user(db_session, user=current_user, todo=True).all()
    if request.method == "POST" and form.validate():
        item = Item(word=form.word.data, user=current_user)
        db_session.add(item)
        db_session.commit()
        return redirect(url_for("index"))
    return render_template(
        "index.html", items=items, form=form, todo_items=todo_items, calendar=calendar
    )


@app.route("/train", methods=["GET", "POST"])
@login_required
def train():
    form = TrainForm(request.form)
    items = get_items_for_user(db_session, user=current_user, todo=True).all()
    if items and request.method == "POST" and form.validate():
        update_item(db_session, items[0], **form.data)
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
            return redirect("/")
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
    return redirect("login")


@app.route("/register", methods=["GET", "POST"])
def register():
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

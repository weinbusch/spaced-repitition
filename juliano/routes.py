from flask import render_template, request, redirect, url_for

from flask_login import login_required, login_user, logout_user, current_user

from .app import app, db_session
from .models import Item
from .forms import ItemForm, TrainForm
from .auth import get_authenticated_user, LoginForm, create_user, RegisterForm
from .spaced_repitition import update_word, get_items_for_user


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ItemForm(request.form)
    items = get_items_for_user(db_session, user=current_user).all()
    todo_items = get_items_for_user(db_session, user=current_user, todo=True).all()
    if request.method == "POST" and form.validate():
        item = Item(word=form.word.data, user=current_user)
        db_session.add(item)
        db_session.commit()
        return redirect(url_for("index"))
    return render_template("index.html", items=items, form=form, todo_items=todo_items)


@app.route("/train", methods=["GET", "POST"])
@login_required
def train():
    form = TrainForm(request.form)
    items = get_items_for_user(db_session, user=current_user, todo=True).all()
    if items and request.method == "POST" and form.validate():
        update_word(items[0], **form.data)
        db_session.commit()
        return redirect(url_for("train"))
    return render_template("train.html", items=items, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = LoginForm(request.form)
        if form.validate():
            credentials = form.data
            user = get_authenticated_user(db_session, **credentials)
            if user:
                login_user(user)
                return redirect("/")
    else:
        form = LoginForm()
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

from flask import render_template, request, redirect, url_for

from flask_login import login_required, login_user, current_user

from .app import app, db_session
from .models import Item
from .forms import ItemForm
from .auth import get_authenticated_user, LoginForm, create_user, RegisterForm


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ItemForm(request.form)
    items = db_session.query(Item).filter_by(user=current_user)
    if request.method == "POST" and form.validate():
        item = Item(word=form.word.data, user=current_user)
        db_session.add(item)
        db_session.commit()
        return redirect(url_for("index"))
    return render_template("index.html", items=items, form=form)


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


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        user = create_user(form.username.data, form.password.data)
        db_session.add(user)
        db_session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

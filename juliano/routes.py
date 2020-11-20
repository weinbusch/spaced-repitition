from flask import render_template, request, redirect

from flask_login import login_required, login_user

from .app import app, db_session
from .auth import get_authenticated_user, LoginForm


@app.route("/")
@login_required
def index():
    return render_template("index.html")


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

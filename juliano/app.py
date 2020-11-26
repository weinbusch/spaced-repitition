from flask import Flask, g
from werkzeug.local import LocalProxy
from flask.logging import default_handler
from flask_wtf.csrf import CSRFProtect


from .db import connect, disconnect, db_logger


db_logger.addHandler(default_handler)


def get_db():
    if "_db" not in g:
        g._db = connect()
    return g._db


db_session = LocalProxy(get_db)


app = Flask(__name__)
app.config["SECRET_KEY"] = open("secret").read()
app.config["WTF_CSRF_TIME_LIMIT"] = None


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("_db", None)
    if db is not None:
        disconnect(db)


csrf = CSRFProtect()
csrf.init_app(app)

from .auth import login_manager  # noqa: E402

login_manager.init_app(app)

import juliano.routes  # noqa: E402, F401

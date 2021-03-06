from flask import Flask, g, current_app
from werkzeug.local import LocalProxy
from flask.logging import default_handler
from flask_wtf.csrf import CSRFProtect

from .db import connect, disconnect, db_logger
from .images import get_random_image

db_logger.addHandler(default_handler)


app = Flask(__name__)

app.config.from_object("juliano.config")

try:
    app.config.from_envvar("JULIANO_SETTINGS")
except RuntimeError:
    pass


def get_db():
    if "_db" not in g:
        g._db = connect(current_app.config["DB_PATH"])
    return g._db


db_session = LocalProxy(get_db)


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("_db", None)
    if db is not None:
        disconnect(db)


csrf = CSRFProtect()
csrf.init_app(app)

from .auth import login_manager  # noqa: E402

login_manager.init_app(app)


@app.context_processor
def animals_processor():
    return dict(get_random_image=get_random_image)


import juliano.routes  # noqa: E402, F401

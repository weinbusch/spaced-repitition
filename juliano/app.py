from flask import Flask, g

from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user

from juliano.db import disconnect, db_session
from juliano.images import get_random_image
from juliano.repo import UserRepository
from juliano.schema import init_mappers
from juliano.routes import router

init_mappers()

csrf = CSRFProtect()


class TokenLoginManager(LoginManager):
    def init_app(self, app, *args, **kwargs):
        super().init_app(app, *args, **kwargs)

        self.login_view = app.config.get("LOGIN_VIEW", "login")

        @app.before_request
        def set_current_user_token():
            if current_user.is_authenticated:
                current_user.get_token()
                db_session.add(current_user)
                db_session.commit()


login_manager = TokenLoginManager()


@login_manager.user_loader
def user_loader(id):
    repo = UserRepository(db_session)
    return repo.get(id)


@login_manager.request_loader
def load_user_from_request(request):
    repo = UserRepository(db_session)
    data = request.headers.get("Authorization", "")
    if data.startswith("Bearer "):
        _, token = data.split("Bearer ", maxsplit=1)
        return repo.get_from_token(token)
    return None


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_object("juliano.config")

    try:
        app.config.from_envvar("JULIANO_SETTINGS")
    except RuntimeError:
        pass

    if config is not None:
        app.config.from_mapping(config)

    @app.teardown_appcontext
    def teardown_db(exception):
        db = g.pop("_db", None)
        if db is not None:
            disconnect(db)

    login_manager.init_app(app)
    csrf.init_app(app)
    router.init_app(app)

    @app.context_processor
    def animals_processor():
        return dict(get_random_image=get_random_image)

    return app


app = create_app()

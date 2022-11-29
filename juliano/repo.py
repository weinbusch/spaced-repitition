from juliano.domain import Item
from juliano.auth import User
from juliano.schema import init_mappers

init_mappers()


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get(self, id):
        return self.session.query(User).get(id)

    def add(self, user):
        self.session.add(user)

    def get_from_token(self, token):
        user = self.session.query(User).filter(User.token == token).one_or_none()
        if user and not user.token_is_expired():
            return user
        return None

    def create_user(self, username, password):
        user = User.create_user(username, password)
        self.add(user)
        return user

    def get_authenticated_user(self, username, password):
        user = self.session.query(User).filter(User.username == username).one_or_none()
        if user and user.verify_password(password):
            return user
        return None

    def list(self):
        return self.session.query(User).all()


class ItemRepository:
    def __init__(self, session):
        self.session = session

    def add(self, item):
        self.session.add(item)

    def get(self, id):
        return self.session.query(Item).get(id)

    def list(self, user):
        return (
            self.session.query(Item)
            .filter(Item.user == user)
            .order_by(Item.next_iteration)
            .all()
        )

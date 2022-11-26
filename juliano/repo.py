from juliano.domain import Item
from juliano.auth import (
    User,
    get_user,
    get_user_from_token,
    get_authenticated_user,
    create_user,
    verify_password,
)


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get(self, id):
        return get_user(self.session, id)

    def add(self, user):
        self.session.add(user)

    def get_from_token(self, token):
        return get_user_from_token(self.session, token)

    def create_user(self, username, password):
        user = create_user(username, password)
        self.add(user)
        return user

    def get_authenticated_user(self, username, password):
        return get_authenticated_user(self.session, username, password)

    def list(self):
        return self.session.query(User).all()


class Repository:
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

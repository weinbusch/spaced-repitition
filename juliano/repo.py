from juliano.domain import Item


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

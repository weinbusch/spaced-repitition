import sqlalchemy as sa
from sqlalchemy.orm import mapper, relationship

from juliano.domain import Item, Event
from juliano.auth import User, Settings

metadata = sa.MetaData()

user_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.Text, unique=True),
    sa.Column("password_hash", sa.Text),
    sa.Column("token", sa.Text, index=True, unique=True),
    sa.Column("token_expires", sa.DateTime),
)

settings_table = sa.Table(
    "settings",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), unique=True),
    sa.Column("max_todo", sa.Integer, default=10),
)

item_table = sa.Table(
    "items",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    sa.Column("word", sa.Text),
    sa.Column("created", sa.DateTime),
    sa.Column("is_active", sa.Boolean),
    sa.Column("easiness_factor", sa.Float),
    sa.Column("inter_repitition_interval", sa.Interval),
    sa.Column("next_iteration", sa.DateTime),
    sa.UniqueConstraint("user_id", "word"),
)

event_table = sa.Table(
    "events",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column(
        "item_id",
        sa.Integer,
        sa.ForeignKey("items.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    sa.Column("grade", sa.Integer),
    sa.Column("created", sa.DateTime),
)


def init_mappers():
    mapper(
        Item,
        item_table,
        properties={
            "events": relationship(Event, lazy="joined"),
            "user": relationship(User, lazy="joined"),
        },
    )
    mapper(Event, event_table)
    mapper(
        User, user_table, properties={"settings": relationship(Settings, uselist=False)}
    )
    mapper(Settings, settings_table)

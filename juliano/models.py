import datetime
import secrets

from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    Float,
    Text,
    DateTime,
    Interval,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from flask_login import UserMixin


Base = declarative_base()


class User(UserMixin, Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    password_hash = Column(Text)
    token = Column(Text, index=True, unique=True)
    token_expires = Column(DateTime)

    def get_id(self):
        return str(self.id)

    def get_token(self):
        now = datetime.datetime.utcnow()
        if not self.token or self.token_expires < now:
            self.token = secrets.token_hex(32)
            self.token_expires = now + datetime.timedelta(seconds=60 * 60 * 24)
        return self.token


class Item(Base):

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    easiness_factor = Column(Float, default=2.5)
    inter_repitition_interval = Column(Interval, default=datetime.timedelta(days=1))
    next_iteration = Column(DateTime)
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("user_id", "word"),)

    user = relationship("User")
    events = relationship(
        "Event",
        order_by="Event.created.desc()",
        cascade="all, delete",
        lazy="joined",
    )

    @property
    def last_learned(self):
        try:
            return self.events[0].created
        except IndexError:
            return None

    @property
    def repitition_number(self):
        return len(self.events)

    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "is_active": self.is_active,
        }

    @property
    def todo(self):
        return (
            self.next_iteration is None
            or self.next_iteration <= datetime.datetime.utcnow()
        )


class Event(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    grade = Column(Integer)
    created = Column(DateTime, default=datetime.datetime.utcnow)

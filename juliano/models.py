import datetime

from sqlalchemy import (
    Column,
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

    def get_id(self):
        return str(self.id)


class Item(Base):

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    repitition_number = Column(Integer, default=0)
    easiness_factor = Column(Float, default=2.5)
    inter_repitition_interval = Column(Interval, default=datetime.timedelta())
    last_learned = Column(DateTime)
    next_iteration = Column(DateTime)

    __table_args__ = (UniqueConstraint("user_id", "word"),)

    user = relationship("User")

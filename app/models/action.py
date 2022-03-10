import datetime
from sqlalchemy.types import DateTime
from sqlalchemy import Column, Integer, String

from helpers.db import Base, SCHEMA


class Action(Base):
    __tablename__ = "action"
    __table_args__ = {'schema': SCHEMA}

    action_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, unique=True)
    action_type = Column(String, nullable=False)
    action_data = Column(String, nullable=False)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<Action(action_id='{self.action_id}', " \
               f"name='{self.name}', " \
               f"action_type='{self.action_type}', " \
               f"action_data='{self.action_data}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "action_id": self.action_id,
            "name": self.name,
            "action_type": self.action_type,
            "action_data": self.action_data,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

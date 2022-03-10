import datetime
from sqlalchemy.types import DateTime
from sqlalchemy import Column, Integer, String, Boolean

from helpers.db import Base, SCHEMA


class Creds(Base):
    __tablename__ = "creds"
    __table_args__ = {'schema': SCHEMA}

    creds_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<Creds(creds_id='{self.creds_id}', " \
               f"name='{self.name}', " \
               f"username='{self.username}', " \
               f"password='{self.password}', " \
               f"is_default='{self.is_default}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "creds_id": self.creds_id,
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "is_default": self.is_default,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

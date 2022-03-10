import datetime
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey

from helpers.db import Base, SCHEMA


class Work(Base):
    __tablename__ = "work"
    __table_args__ = {'schema': SCHEMA}

    work_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state_id = Column(Integer, ForeignKey(f"{SCHEMA}.state.state_id"))
    device_uid = Column(String, nullable=False)
    actions = Column(JSON, nullable=False)
    trigger = Column(String, nullable=False)
    requires_console = Column(Boolean, nullable=False)
    assigned = Column(DateTime)
    status = Column(String, nullable=False, default="PENDING")
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    state = relationship("State", back_populates="works", uselist=False)
    executions = relationship("Execution", back_populates="work", uselist=True)

    def __repr__(self):
        return f"<Work(work_id='{self.work_id}', " \
               f"state_id='{self.state_id}', " \
               f"device_uid='{self.device_uid}', " \
               f"actions='{self.actions}', " \
               f"trigger='{self.trigger}', " \
               f"requires_console='{self.requires_console}', " \
               f"assigned='{self.assigned}', " \
               f"status='{self.status}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "work_id": self.work_id,
            "state_id": self.state_id,
            "device_uid": self.device_uid,
            "actions": self.actions,
            "trigger": self.trigger,
            "requires_console": self.requires_console,
            "assigned": self.assigned.isoformat() if self.assigned else None,
            "status": self.status,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

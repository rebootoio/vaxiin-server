import datetime
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON

from helpers.db import Base, SCHEMA


class Execution(Base):
    __tablename__ = "execution"
    __table_args__ = {'schema': SCHEMA}

    execution_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    work_id = Column(Integer, ForeignKey(f"{SCHEMA}.work.work_id"), nullable=False)
    state_id = Column(Integer, ForeignKey(f"{SCHEMA}.state.state_id"))
    action_name = Column(String, nullable=False)
    trigger = Column(String, nullable=False)
    status = Column(String, nullable=False)
    run_data = Column(JSON, nullable=False)
    elapsed_time = Column(Float(precision=3), nullable=False)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    work = relationship("Work", back_populates="executions", uselist=False)
    state = relationship("State", back_populates="executions", uselist=False)

    def __repr__(self):
        return f"<Execution(execution_id='{self.execution_id}', " \
               f"work_id='{self.work_id}', " \
               f"state_id='{self.state_id}', " \
               f"action_name='{self.action_name}', " \
               f"trigger='{self.trigger}', " \
               f"status='{self.status}', " \
               f"run_data='{self.run_data}', " \
               f"elapsed_time='{self.elapsed_time}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "execution_id": self.execution_id,
            "work_id": self.work_id,
            "state_id": self.state_id,
            "action_name": self.action_name,
            "trigger": self.trigger,
            "status": self.status,
            "run_data": self.run_data,
            "elapsed_time": self.elapsed_time,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

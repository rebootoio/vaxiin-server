import datetime
from sqlalchemy.types import DateTime
from sqlalchemy import Column, String, Boolean, JSON

from helpers.db import Base, SCHEMA


class Device(Base):
    __tablename__ = "device"
    __table_args__ = {'schema': SCHEMA}

    uid = Column(String, primary_key=True, index=True)
    ipmi_ip = Column(String, nullable=False)
    creds_name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    zombie = Column(Boolean, nullable=False, default=False)
    device_metadata = Column(JSON, nullable=False, default={})
    heartbeat_timestamp = Column(DateTime)
    agent_version = Column(String)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<Device(uid='{self.uid}', " \
               f"ipmi_ip='{self.ipmi_ip}', " \
               f"creds_name='{self.creds_name}', " \
               f"model='{self.model}', " \
               f"zombie='{self.zombie}', " \
               f"device_metadata='{self.device_metadata}', " \
               f"heartbeat_timestamp='{self.heartbeat_timestamp}', " \
               f"agent_version='{self.agent_version}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "uid": self.uid,
            "ipmi_ip": self.ipmi_ip,
            "creds_name": self.creds_name,
            "model": self.model,
            "zombie": self.zombie,
            "metadata": self.device_metadata,
            "heartbeat_timestamp": self.heartbeat_timestamp.isoformat() if self.heartbeat_timestamp else None,
            "agent_version": self.agent_version,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

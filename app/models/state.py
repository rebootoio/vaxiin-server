import datetime
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, LargeBinary, Boolean, ForeignKey

from helpers.db import Base, SCHEMA
import helpers.image as image_helper


class State(Base):
    __tablename__ = "state"
    __table_args__ = {'schema': SCHEMA}

    state_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    screenshot = Column(LargeBinary, nullable=False)
    ocr_text = Column(String, nullable=False)
    device_uid = Column(String, nullable=False)
    resolved = Column(Boolean, nullable=False, default=False)
    matched_rule = Column(Integer, ForeignKey(f"{SCHEMA}.rule.name"), nullable=True)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    works = relationship("Work", back_populates="state", uselist=True)
    executions = relationship("Execution", back_populates="state", uselist=True)

    def __repr__(self):
        return f"<State(state_id='{self.state_id}', " \
               f"screenshot_type='{type(self.screenshot)}', " \
               f"ocr_text='{self.ocr_text}', " \
               f"device_uid='{self.device_uid}', " \
               f"resolved='{self.resolved}', " \
               f"matched_rule='{self.matched_rule}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "state_id": self.state_id,
            "screenshot": image_helper.encode_image(self.screenshot),
            "ocr_text": self.ocr_text,
            "device_uid": self.device_uid,
            "resolved": self.resolved,
            "matched_rule": self.matched_rule,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

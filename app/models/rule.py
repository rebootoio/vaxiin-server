import datetime
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON

from helpers.db import Base, SCHEMA


class RuleOrder(Base):
    __tablename__ = 'rule_order'
    __table_args__ = {'schema': SCHEMA}

    rule_order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=True)

    rules = relationship("Rule", order_by="Rule.position", collection_class=ordering_list('position', count_from=1, reorder_on_append=True))


class Rule(Base):
    __tablename__ = "rule"
    __table_args__ = {'schema': SCHEMA}

    rule_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    state_id = Column(Integer, ForeignKey(f"{SCHEMA}.state.state_id"), nullable=False)
    regex = Column(String, nullable=False)
    actions = Column(JSON, nullable=False)
    ignore_case = Column(Boolean, nullable=False, default=True)
    enabled = Column(Boolean, nullable=False, default=True)
    position = Column(Integer)
    rule_order_id = Column(Integer, ForeignKey(f"{SCHEMA}.rule_order.rule_order_id"), nullable=False)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)

    state = relationship("State", back_populates="rule", uselist=False, foreign_keys=[state_id])

    def __repr__(self):
        return f"<Rule(rule_id='{self.rule_id}', " \
               f"name='{self.name}', " \
               f"state_id='{self.state_id}', " \
               f"regex='{self.regex}', " \
               f"actions='{self.actions}', " \
               f"ignore_case='{self.ignore_case}', " \
               f"enabled='{self.enabled}', " \
               f"position='{self.position}', " \
               f"last_updated='{self.last_updated}', " \
               f"created_at='{self.created_at}')>"

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "state_id": self.state_id,
            "regex": self.regex,
            "actions": self.actions,
            "ignore_case": self.ignore_case,
            "enabled": self.enabled,
            "position": self.position,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }

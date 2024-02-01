import uuid

from sqlalchemy import Column, VARCHAR, DOUBLE, ForeignKey
from sqlalchemy.orm import relationship

from geo.db import Base
from geo.utils.sa import GUID


class Event(Base):
    __tablename__ = "events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    network = Column(VARCHAR(32), nullable=False)
    x = Column(DOUBLE(), nullable=False)
    y = Column(DOUBLE(), nullable=False)
    z = Column(DOUBLE(), nullable=False)

    task_id = Column(GUID(), ForeignKey("tasks.id", ondelete="cascade"), nullable=False)
    task = relationship("Task", back_populates="events")
    detections = relationship("Detection", back_populates="event")

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
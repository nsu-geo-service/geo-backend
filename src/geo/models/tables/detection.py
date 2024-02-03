import uuid

from sqlalchemy import Column, DOUBLE, ForeignKey, Enum, func, DateTime
from sqlalchemy.orm import relationship

from geo.db import Base
from geo.models.schemas import Phase
from geo.utils.sa import GUID


class Detection(Base):
    __tablename__ = "detections"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    phase = Column(Enum(Phase), nullable=False)
    time = Column(DOUBLE(), nullable=False)

    station_id = Column(GUID(), ForeignKey("stations.id", ondelete="cascade"), nullable=False)
    station = relationship("Station", back_populates="detections")

    event_id = Column(GUID(), ForeignKey("events.id", ondelete="cascade"), nullable=False)
    event = relationship("Event", back_populates="detections")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

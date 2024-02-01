import uuid

from sqlalchemy import Column, DateTime, VARCHAR, DOUBLE, ForeignKey
from sqlalchemy.orm import relationship

from geo.db import Base
from geo.utils.sa import GUID


class SeisData(Base):
    __tablename__ = "seisdata"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    network = Column(VARCHAR(32), nullable=False)
    min_latitude = Column(DOUBLE(), nullable=True)
    max_latitude = Column(DOUBLE(), nullable=True)
    min_longitude = Column(DOUBLE(), nullable=True)
    max_longitude = Column(DOUBLE(), nullable=True)

    task_id = Column(GUID(), ForeignKey("tasks.id", ondelete="cascade"), nullable=False)
    task = relationship("Task", back_populates="seisdata", uselist=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

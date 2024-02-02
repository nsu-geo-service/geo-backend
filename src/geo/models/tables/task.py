import uuid

from sqlalchemy import Column, Enum, DateTime, func
from sqlalchemy.orm import relationship

from geo.db import Base
from geo.models.schemas import TaskState, TaskStep
from geo.utils.sa import GUID


class Task(Base):
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    state = Column(Enum(TaskState), default=TaskState.PLAIN, nullable=False)
    step = Column(Enum(TaskStep), nullable=True)

    stations = relationship("Station", back_populates="task")
    events = relationship("Event", back_populates="task")
    seisdata = relationship("SeisData", back_populates="task", uselist=False)
    tomography = relationship("Tomography", back_populates="task", uselist=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_in = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

import uuid

from sqlalchemy import Column, DOUBLE, ForeignKey, Integer, ARRAY, PickleType
from sqlalchemy.orm import relationship

from geo.db import Base
from geo.utils.sa import GUID


class Tomography(Base):
    """
    Модель таблицы tomography


    WARNING: Модель описана под Sqlite, из-за чего используется для
    хранения массивов PickleType. В случае использования другой СУБД
    необходимо заменить PickleType на ARRAY.

    """
    __tablename__ = "tomography"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    iter_max = Column(Integer, nullable=False)
    lin_sys_LSQR_iter_max = Column(Integer, nullable=False)
    mat_damping_P = Column(DOUBLE, nullable=False)
    mat_damping_P4V = Column(DOUBLE, nullable=False)
    mat_damping_S = Column(DOUBLE, nullable=False)
    mat_damping_S4V = Column(DOUBLE, nullable=False)
    mat_damping_HP = Column(DOUBLE, nullable=False)
    mat_damping_HP4V = Column(DOUBLE, nullable=False)
    mat_damping_HS = Column(DOUBLE, nullable=False)
    mat_damping_HS4V = Column(DOUBLE, nullable=False)
    mat_damping_VP = Column(DOUBLE, nullable=False)
    mat_damping_VP4V = Column(DOUBLE, nullable=False)
    mat_damping_VS = Column(DOUBLE, nullable=False)
    mat_damping_VS4V = Column(DOUBLE, nullable=False)
    mat_srcs_psv_corr_H = Column(DOUBLE, nullable=False)
    mat_srcs_psv_corr_I = Column(DOUBLE, nullable=False)
    mat_srcs_psv_corr_V = Column(DOUBLE, nullable=False)
    v_limits_p = Column(PickleType, nullable=False)
    v_limits_s = Column(PickleType, nullable=False)
    grid_size = Column(PickleType, nullable=False)
    grid_step = Column(PickleType, nullable=False)
    base_model = Column(PickleType, nullable=False)

    task_id = Column(GUID(), ForeignKey("tasks.id", ondelete="cascade"), nullable=False)
    task = relationship("Task", back_populates="tomography")

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

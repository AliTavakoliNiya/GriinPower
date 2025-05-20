from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models import Base


class PLC(Base):
    __tablename__ = 'plc'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=True)
    order_number = Column(String, unique=True, nullable=True)
    series = Column(String, nullable=True)
    model = Column(String, nullable=True)

    n_di = Column(Integer, nullable=True)
    n_do = Column(Integer, nullable=True)
    n_ai = Column(Integer, nullable=True)
    n_ao = Column(Integer, nullable=True)

    has_prof_inet = Column(Integer, nullable=True)  # stored as 0 or 1
    has_prof_ibus = Column(Integer, nullable=True)

    max_modules_per_rack = Column(Integer, nullable=True)
    support_8_channel = Column(Integer, nullable=True)
    support_16_channel = Column(Integer, nullable=True)
    support_32_channel = Column(Integer, nullable=True)

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)


    # Relationships
    item = relationship("Item", back_populates="plc", uselist=False)
    modified_user = relationship("User", back_populates="plcs_modified")


    def __repr__(self):
        return ( f"PLC(order_number={self.order_number}, model={self.model}, series={self.series}" )

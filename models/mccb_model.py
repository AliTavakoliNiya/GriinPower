from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import  Base

class MCCB(Base):
    __tablename__ = 'mccb'

    mccb_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)
    mccb_reference = Column(String, nullable=False, unique=True)
    p_kw = Column(Float, nullable=False)
    i_a = Column(Float, nullable=False)
    brand = Column(String, nullable=False)

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
    modified_at = Column(String, nullable=False)

    item = relationship("Item", back_populates="mccb", uselist=False)
    modified_user = relationship("User", back_populates="mccbs_modified")

    def __repr__(self):
        return (
            f"<MCCB(p_kw={self.p_kw}, i_a={self.i_a}, "
            f"reference='{self.mccb_reference}', brand='{self.brand}')>"
        )

def get_mccb_by_motor_power(p_kw_value):
    session = SessionLocal()
    try:
        return session.query(MCCB).filter(MCCB.p_kw == p_kw_value).order_by(MCCB.p_kw.asc()).first() or MCCB()
    except Exception as e:
        session.rollback()
        show_message("---------------------------------------------\n" + str(e) + "\n")
        return MCCB()
    finally:
        session.close()

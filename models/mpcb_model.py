from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import  Base

class MPCB(Base):
    __tablename__ = 'mpcb'

    mpcb_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False)
    mpcb_reference = Column(String, nullable=False, unique=True)
    p_kw = Column(Float, nullable=False)
    ie_a = Column(Float, nullable=False)
    iq_ka = Column(Float, nullable=False)
    min_current_range_a = Column(Float, nullable=False)
    max_current_range_a = Column(Float, nullable=False)
    brand = Column(String, nullable=False)

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
    modified_at = Column(String, nullable=False)

    item = relationship("Item", back_populates="mpcb", uselist=False)
    modified_user = relationship("User", back_populates="mpcbs_modified")

    def __repr__(self):
        return (
            f"Motor Power(KW)={self.p_kw}, "
            f"Ie(A)={self.ie_a}, "  # Fixed spelling error
            f"Iq(KA)={self.iq_ka}, "
            f"MPCB Reference={self.mpcb_reference}, "
            f"Minimum Current(A)={self.min_current_range_a}, "
            f"Maximum Current(A)={self.max_current_range_a}, "
            f"Brand={self.brand}"
        )


def get_mpcb_by_motor_power(p_kw_value):
    session = SessionLocal()
    try:
        return session.query(MPCB).filter(MPCB.p_kw == p_kw_value).order_by(MPCB.p_kw.asc()).first() or MPCB()
    except Exception as e:
        session.rollback()
        show_message(f"---------------------------------------------\n{str(e)}\n", "Error")
        return MPCB()
    finally:
        session.close()

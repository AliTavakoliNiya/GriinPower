from sqlalchemy import Column, Integer, Float, String

from utils.database import Base, SessionLocal
from views.message_box_view import show_message


class MPCB(Base):
    __tablename__ = 'mpcb'

    id = Column(Integer, primary_key=True, autoincrement=True)
    p_kw = Column(Float, nullable=False)
    ie_a = Column(Float, nullable=False)
    iq_ka = Column(Float, nullable=False)
    mpcb_reference = Column(String, nullable=False)
    min_current_range_a = Column(Float, nullable=False)
    max_current_range_a = Column(Float, nullable=False)
    brand = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"Motor Power(KW)={self.p_kw}, "
            f"Ie(A)={self.ie_a}, "
            f"Iq(KA)={self.iq_ka}, "
            f"MPCB Reference={self.mpcb_reference}', "
            f"Minimum Current(A)={self.min_current_range_a}, "
            f"Maximum Current(A)={self.max_current_range_a}, "
            f"Brand={self.brand}"
        )


def get_mpcb_by_motor_power(p_kw_value):
    session = SessionLocal()
    try:
        session.begin()
        rslt = session.query(MPCB).filter(MPCB.p_kw == p_kw_value).order_by(MPCB.p_kw.asc()).first()
        if rslt:
            session.refresh(rslt)
            mpcb = MPCB()
            mpcb.p_kw = rslt.p_kw
            mpcb.ie_a = rslt.ie_a
            mpcb.iq_ka = rslt.iq_ka
            mpcb.mpcb_reference = rslt.mpcb_reference
            mpcb.min_current_range_a = rslt.min_current_range_a
            mpcb.max_current_range_a = rslt.max_current_range_a
            mpcb.brand = rslt.brand
            return mpcb
        return MPCB()
    except Exception as e:
        session.rollback()
        show_message("---------------------------------------------\n"+str(e)+"\n")
        return MPCB()
    finally:
        session.close()

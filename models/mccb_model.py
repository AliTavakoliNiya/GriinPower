from sqlalchemy import Column, Integer, Float, String

from utils.database import Base, SessionLocal
from views.message_box_view import show_message


class MCCB(Base):
    __tablename__ = 'mccb'

    id = Column(Integer, primary_key=True, autoincrement=True)
    p_kw = Column(Float, nullable=False)
    i_a = Column(Float, nullable=False)
    mccb_reference = Column(String, nullable=False)
    brand = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"Motor Power(KW)={self.p_kw}, "
            f"Current (A)={self.i_a}, "
            f"MCCB Reference={self.mccb_reference}, "
            f"Brand={self.brand}"
        )


def get_mccb_by_motor_power(p_kw_value):
    session = SessionLocal()
    try:
        session.begin()
        rslt = session.query(MCCB).filter(MCCB.p_kw == p_kw_value).order_by(MCCB.p_kw.asc()).first()
        if rslt:
            session.refresh(rslt)
            mccb = MCCB()
            mccb.p_kw = rslt.p_kw
            mccb.i_a = rslt.i_a
            mccb.mccb_reference = rslt.mccb_reference
            mccb.brand = rslt.brand
            return mccb
        return MCCB()
    except Exception as e:
        session.rollback()
        show_message("---------------------------------------------\n"+str(e)+"\n")
        return MCCB()
    finally:
        session.close()

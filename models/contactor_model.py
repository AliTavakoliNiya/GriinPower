from sqlalchemy import Column, Integer, Float, String

from utils.database import Base, SessionLocal
from views.message_box_view import show_message


class Contactor(Base):
    __tablename__ = 'contactor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    p_kw = Column(Float, nullable=False)
    contactor_reference = Column(String, nullable=False)
    brand = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"Motor Power(KW)={self.p_kw}, "
            f"Contactor Reference={self.contactor_reference}', "
            f"Brand={self.brand}"
        )


def get_contactor_by_motor_power(p_kw_value):
    session = SessionLocal()
    try:
        session.begin()
        rslt = session.query(Contactor).filter(Contactor.p_kw == p_kw_value).order_by(Contactor.p_kw.asc()).first()
        if rslt:
            # Ensure all attributes are loaded before session closes
            session.refresh(rslt)
            # Create a new Contactor instance with the loaded values
            contactor = Contactor()
            contactor.p_kw = rslt.p_kw
            contactor.contactor_reference = rslt.contactor_reference
            contactor.brand = rslt.brand
            return contactor
        else:
            return Contactor()
    except Exception as e:
        session.rollback()
        show_message("---------------------------------------------\n" + str(e) + "\n")
        return Contactor()
    finally:
        session.close()

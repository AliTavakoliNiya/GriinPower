from sqlalchemy import Column, Integer, Float, String
from utils.database import Base, engine, SessionLocal
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

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

def get_contactor_by_motor_power(p_kw_value):
    try:
        session = SessionLocal()
        rslt = session.query(Contactor).filter(Contactor.p_kw == p_kw_value).order_by(Contactor.p_kw.asc()).first()
        if rslt:
            return rslt
        else:
            return Contactor()
    except Exception as e:
        show_message("---------------------------------------------\n" + str(e) + "\n")
        return Contactor()
    finally:
        session.close()




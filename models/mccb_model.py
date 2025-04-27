from sqlalchemy import Column, Integer, Float, String
from utils.database import Base, engine, SessionLocal


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


# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

def get_mccb_by_motor_power(p_kw_value):
    try:
        session = SessionLocal()
        return session.query(MCCB).filter(MCCB.p_kw >= p_kw_value).order_by(MCCB.p_kw.asc()).first()
    except:
        return []
    finally:
        session.close()

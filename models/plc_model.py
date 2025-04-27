from sqlalchemy import Column, Integer, String
from utils.database import Base, engine, SessionLocal


class PLC(Base):
    __tablename__ = 'plc'

    id = Column(Integer, primary_key=True, autoincrement=True)
    series = Column(String, nullable=False)
    model = Column(String, nullable=False)
    order_number = Column(String, nullable=False)
    di = Column(Integer, nullable=False)
    do = Column(Integer, nullable=False)
    ai = Column(Integer, nullable=False)
    ao = Column(Integer, nullable=False)
    has_profinet = Column(Integer, nullable=False)  # Typically 0/1 (boolean-ish)
    has_profibus = Column(Integer, nullable=False)
    max_modules_per_rack = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            f"<PLC(id={self.id}, "
            f"series='{self.series}' (PLC series), "
            f"model='{self.model}' (PLC model), "
            f"order_number='{self.order_number}' (Order number), "
            f"di={self.di} (Number of digital inputs), "
            f"do={self.do} (Number of digital outputs), "
            f"ai={self.ai} (Number of analog inputs), "
            f"ao={self.ao} (Number of analog outputs), "
            f"has_profinet={self.has_profinet} (Has Profinet, typically 0/1), "
            f"has_profibus={self.has_profibus} (Has Profibus, typically 0/1), "
            f"max_modules_per_rack={self.max_modules_per_rack} (Max modules per rack)>"
        )


# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)


def get_plc_by_series(series):
    session = SessionLocal()
    try:
        return session.query(PLC).filter(PLC.series == series).first()
    finally:
        session.close()

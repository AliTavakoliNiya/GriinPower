from sqlalchemy import Column, Integer, String

from utils.database import Base, SessionLocal
from views.message_box_view import show_message


class General(Base):
    __tablename__ = 'general'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String)

    def __repr__(self):
        return f"{self.name}"


def get_general_by_name(name):
    session = SessionLocal()
    try:
        session.begin()
        rslt = session.query(General).filter(General.name == name).first()
        if rslt:
            session.refresh(rslt)
            general = General()
            general.name = rslt.name
            general.brand = rslt.brand
            return general
        return General()
    except Exception as e:
        session.rollback()
        show_message("---------------------------------------------\n"+str(e)+"\n")
        return General()
    finally:
        session.close()

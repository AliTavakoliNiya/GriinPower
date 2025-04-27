from sqlalchemy import Column, Integer, Float, String
from utils.database import Base, engine, SessionLocal
from views.message_box_view import show_message


class General(Base):
    __tablename__ = 'general'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String)

    def __repr__(self):
        return f"{self.name}"


# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)


def get_general_by_name(name):
    global session
    try:
        session = SessionLocal()
        rslt =  session.query(General).filter(General.name == name).first()
        if rslt:
            return rslt
        else:
            return General()
    except Exception as e:
        show_message("---------------------------------------------\n"+str(e)+"\n")
        return General()
    finally:
        session.close()
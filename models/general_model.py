from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import Base, User

class General(Base):
    __tablename__ = 'general'

    general_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    spec = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
    modified_at = Column(String, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="general", uselist=False)
    modified_user = relationship("User", back_populates="generals_modified")

    def __repr__(self):
        return f"<General(name='{self.name}', brand='{self.brand}')>"


def get_general_by_name(name):
    session = SessionLocal()
    try:
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

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from utils.database import SessionLocal
from views.message_box_view import show_message
from models import Base


class Instrument(Base):
    __tablename__ = 'instrument'

    instruments_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)
    type = Column(Integer, nullable=False)
    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=False)
    modified_at = Column(String, nullable=False)
    note = Column(String, nullable=True)

    # Relationships
    item = relationship("Item", back_populates="instrument", uselist=False)
    modified_user = relationship("User", back_populates="instruments_modified")

    def __repr__(self):
        return f"<Instrument(type={self.type}')>"

def get_instrument_by_type(type_value):
    session = SessionLocal()
    try:
        return session.query(Instrument).filter(Instrument.type == type_value).first() or Instrument()
    except Exception as e:
        session.rollback()
        show_message("instrument_model\n" + str(e) + "\n")
        return Instrument()
    finally:
        session.close()

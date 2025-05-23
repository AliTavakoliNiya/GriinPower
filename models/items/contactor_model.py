from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import Base


class Contactor(Base):
    __tablename__ = 'contactor'

    contactor_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete="CASCADE"), nullable=False, unique=True)

    current_a = Column(Float, nullable=False)

    modified_by = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
    modified_at = Column(String, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="contactor", uselist=False)
    modified_user = relationship("User", back_populates="contactors_modified")

    def __repr__(self):
        return f"<Contactor(current_a={self.current_a})>"


def get_contactor_by_current(current_a_value: float):
    session = SessionLocal()
    try:
        contactor = (
            session.query(Contactor)
            .filter(Contactor.current_a >= current_a_value)
            .order_by(Contactor.current_a.asc())
            .first()
        )
        return contactor or Contactor()
    except Exception as e:
        session.rollback()
        show_message(f"contactor_model\n{str(e)}\n")
        return Contactor()
    finally:
        session.close()

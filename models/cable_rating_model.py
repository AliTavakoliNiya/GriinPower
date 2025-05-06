from sqlalchemy import Column, Float, Integer, String

from utils.database import Base, SessionLocal
from views.message_box_view import show_message


class CableRating(Base):
    __tablename__ = 'cable_rating'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cable_size_mm = Column(Float, nullable=False)
    cable_length_m = Column(Float, nullable=False)
    cable_current_a = Column(Float, nullable=False)
    cable_material = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"Size(mm)={self.cable_size_mm}, "
            f"Length(m)={self.cable_length_m}, "
            f"Current(A)={self.cable_current_a}, "
            f"Material={self.cable_material}"
        )


def get_cable_by_dimension_current(length, current):
    session = SessionLocal()
    try:
        session.begin()
        rslt = (session.query(CableRating)
                .filter(CableRating.cable_length_m >= length,
                       CableRating.cable_current_a >= current)
                .order_by(CableRating.cable_length_m.asc(),
                         CableRating.cable_current_a.asc())
                .first())
        if rslt:
            session.refresh(rslt)
            cable = CableRating()
            cable.cable_size_mm = rslt.cable_size_mm
            cable.cable_length_m = rslt.cable_length_m
            cable.cable_current_a = rslt.cable_current_a
            cable.cable_material = rslt.cable_material
            return cable
        return CableRating()
    except Exception as e:
        session.rollback()
        show_message("---------------------------------------------\n" + str(e) + "\n")
        return CableRating()
    finally:
        session.close()

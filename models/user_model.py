import jdatetime
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import Base
import hashlib


def now_jalali():
    return jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    role = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=now_jalali)

    contactors_modified = relationship("Contactor", back_populates="modified_user")
    mpcbs_modified = relationship("MPCB", back_populates="modified_user")
    mccbs_modified = relationship("MCCB", back_populates="modified_user")
    generals_modified = relationship("General", back_populates="modified_user")
    instruments_modified = relationship("Instrument", back_populates="modified_user")
    item_prices_created = relationship("ItemPrice", back_populates="creator")
    plcs_modified = relationship("PLC", back_populates="modified_user")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


def get_user_by_username(username: str, password: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            # print(hashed_password)
            if user.password == hashed_password:
                return user
            else:
                show_message(f"password is incorrect", "login failed")
        else:
            show_message(f"user not found", "login failed")

    except Exception as e:
        session.rollback()
        show_message(f"somthing went wrong\n {str(e)}", "Error")
        return None
    finally:
        session.close()

import jdatetime
from sqlalchemy import Column, String, Integer
from utils.database import SessionLocal
from views.message_box_view import show_message
from models import Base
import hashlib


def now_jalali():
    return jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    role = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=now_jalali)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

def get_all_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return True, users
    except Exception as e:
        session.rollback()
        show_message(f"Something went wrong while fetching users:\n{str(e)}", "Error")
        return False, []
    finally:
        session.close()



def get_user_by_username(username: str, password: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
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

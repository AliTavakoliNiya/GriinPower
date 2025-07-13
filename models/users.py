import jdatetime
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from utils.database import SessionLocal
from models import Base
import hashlib

def now_jalali():
    return jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    role = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=now_jalali)

    modified_documents = relationship("Document", back_populates="modified_by", lazy="joined")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

def get_all_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return True, users
    except Exception as e:
        session.rollback()
        return False, f"Error fetching users: {str(e)}"
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
        return None
    except Exception as e:
        session.rollback()
        print(f"Error fetching user: {str(e)}")
        return None
    finally:
        session.close()

def create_or_update_user(user):
    session = SessionLocal()
    try:
        if user.id:
            existing_user = session.query(User).filter(User.id == user.id).first()
            if not existing_user:
                return False, "User not found for update."

            existing_user.username = user.username
            existing_user.first_name = user.first_name
            existing_user.last_name = user.last_name
            existing_user.phone = user.phone
            existing_user.email = user.email
            existing_user.role = user.role

            if user.password:
                # Only hash if it's not already 64 characters (i.e. not already SHA-256 hex)
                if len(user.password) != 64 or not all(c in '0123456789abcdef' for c in user.password.lower()):
                    user.password = hashlib.sha256(user.password.encode()).hexdigest()
                existing_user.password = user.password
        else:
            if session.query(User).filter(User.username == user.username).first():
                return False, "Username already exists."

            if user.email and session.query(User).filter(User.email == user.email).first():
                return False, "Email already exists."

            if not user.password:
                return False, "Password is required for new users."

            hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
            user.password = hashed_pw
            session.add(user)

        session.commit()
        return True, "User saved successfully."
    except Exception as e:
        session.rollback()
        return False, f"Error saving user: {str(e)}"
    finally:
        session.close()

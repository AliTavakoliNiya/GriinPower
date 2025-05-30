from sqlalchemy import Column, Integer, String, DateTime
from models.items import Base

import jdatetime
today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d %H:%M")



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    role = Column(String, default='user')
    created_at = Column(DateTime, default=today_shamsi)

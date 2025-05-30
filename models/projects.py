

from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship

from models import Base

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    client = Column(String)
    start_date = Column(Date)
    description = Column(Text)

    usages = relationship('ProjectComponent', back_populates='project', cascade="all, delete-orphan")
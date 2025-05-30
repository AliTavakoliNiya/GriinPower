

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.items import Base

class ProjectComponent(Base):
    __tablename__ = 'project_components'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    component_id = Column(Integer, ForeignKey('components.id'))
    quantity = Column(Integer)

    project = relationship('Project', back_populates='usages')
    component = relationship('Component')
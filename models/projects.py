from sqlalchemy import Column, ForeignKey, Integer, String, Text
import json

from sqlalchemy.orm import relationship

from models.abs_motor import Motor
from utils.database import SessionLocal
import jdatetime
import traceback
from models import Base


def now_jalali():
    return jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String)
    unique_no = Column(String, unique=True)
    revision = Column(Integer)
    modified_by_id = Column(Integer, ForeignKey("users.id"))
    modified_at = Column(String, default=now_jalali)
    project_electrical_specs = Column(Text)

    # Relationships
    modified_by = relationship("User")

    def serialize_project_data(self, data: dict) -> dict:
        def convert(obj):
            if isinstance(obj, Motor):
                return {"Motor": str(obj)}
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj

        return convert(data)

    def set_data(self, data_dict: dict):
        self.project_electrical_specs = json.dumps(self.serialize_project_data(data_dict))

    def __repr__(self):
        return f"<Project id={self.id} name='{self.name}' code='{self.code}'>"


def save_project(current_project):
    saving_project = Project()
    saving_project.id = current_project.id
    saving_project.name = current_project.name
    saving_project.code = current_project.code
    saving_project.unique_no = current_project.unique_no
    saving_project.revision = current_project.revision
    saving_project.modified_by_id = current_project.modified_by_id
    saving_project.modified_at = now_jalali()
    saving_project.set_data(current_project.project_electrical_specs)

    session = SessionLocal()
    try:
        if saving_project.id:  # update existing
            session.query(Project).filter(Project.id == saving_project.id).update({
                Project.modified_by_id: saving_project.modified_by_id,
                Project.modified_at: saving_project.modified_at,
                Project.project_electrical_specs: saving_project.project_electrical_specs,
            })
        else:  # save new revision as new record
            session.add(saving_project)

        session.commit()
        return True, "Successfully saved!"
    except Exception as e:
        session.rollback()
        print(traceback.format_exc())
        return False, f"Error Saving Project\n{str(e)}"
    finally:
        session.close()


def get_project(project_id=None, code=None, unique_no=None, revision=None):
    session = SessionLocal()
    try:
        query = session.query(Project)

        # Apply filters dynamically if parameters are provided
        if project_id is not None:
            query = query.filter(Project.id == project_id)
        if code is not None:
            query = query.filter(Project.code == code)
        if unique_no is not None:
            query = query.filter(Project.unique_no == unique_no)

        # Apply revision filter if provided, otherwise get the latest revision
        if revision is not None:
            query = query.filter(Project.revision == revision)
        else:
            query = query.order_by(Project.revision.desc())

        project = query.first()

        if project is None:
            return False, "Project not found"

        return True, project
    except Exception as e:
        print(traceback.format_exc())
        return False, f"Error loading project\n{str(e)}"
    finally:
        session.close()


def get_all_project():
    session = SessionLocal()
    try:
        projects = session.query(Project).all()
        return True, projects
    except Exception as e:
        session.rollback()
        print(traceback.format_exc())
        return False, f"Error fetching projects\n{str(e)}"
    finally:
        session.close()

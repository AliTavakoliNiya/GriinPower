from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
import json
from models.abs_motor import Motor
from utils.database import SessionLocal
import jdatetime
import traceback


Base = declarative_base()
today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String)
    unique_no = Column(String)
    revison = Column(String)
    modified_by_id = Column(Integer)
    modified_at = Column(String)
    project_electrical_specs = Column(Text)

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


def save_project(current_project, new_revision=None):
    saving_project = Project()
    saving_project.name = current_project.name
    saving_project.code = current_project.code
    saving_project.unique_no = current_project.unique_no
    saving_project.revison = current_project.revison
    saving_project.modified_by_id = current_project.modified_by_id
    saving_project.modified_at = today_shamsi
    saving_project.set_data(current_project.project_electrical_specs)

    session = SessionLocal()
    try:
        if new_revision:  # save new revision as new record
            saving_project.id = None
            saving_project.revison = new_revision
            session.add(saving_project)
        else:  # update existing
            saving_project.id = current_project.id
            session.query(Project).filter(Project.id == saving_project.id).update({
                Project.modified_by_id: saving_project.modified_by_id,
                Project.modified_at: saving_project.modified_at,
                Project.project_electrical_specs: saving_project.project_electrical_specs,
            })
        session.commit()
        return True, "Successfully saved!"
    except Exception as e:
        session.rollback()
        print(traceback.format_exc())
        return False, f"Error Saving Project\n{str(e)}"
    finally:
        session.close()


def get_project(project_id: int):
    session = SessionLocal()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return False, "Project not found"
        loaded_project = json.loads(project.project_electrical_specs)
        return True, loaded_project
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

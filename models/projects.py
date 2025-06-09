from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
import json
from models.abs_motor import Motor

from utils.database import SessionLocal

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String)
    unique_no = Column(String)
    revison = Column(String)
    datas = Column(Text)

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
        self.datas = json.dumps(self.serialize_project_data(data_dict))


def save_project(new_project):
    session = SessionLocal()
    try:
        session.add(new_project)
        session.commit()
        return True, "Successfully saved project"
    except Exception as e:
        session.rollback()
        return False, f"Error saving project\n{str(e)}"
    finally:
        session.close()


def get_project(project_id: int):
    session = SessionLocal()
    try:
        project = session.query(Project).first()
        loaded_project = json.loads(project.datas)
        return True, loaded_project
    except Exception as e:
        print(str(e))
        return False, f"Error loading project\n{str(e)}"
    finally:
        session.close()

    session.close()

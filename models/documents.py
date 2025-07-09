import os
import traceback

import jdatetime
from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String, Text
from models import Base
from sqlalchemy.orm import relationship

from utils.database import SessionLocal

today_shamsi = jdatetime.datetime.today().strftime("%Y/%m/%d %H:%M")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project_unique_no = Column(Integer, ForeignKey("projects.unique_no"), nullable=True)  # nullable since not NOT NULL in schema
    revision = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    modified_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    modified_at = Column(String, nullable=False)
    note = Column(Text, nullable=True)

    # relationships
    project = relationship("Project", back_populates="documents")
    project_by_unique_no = relationship("Project")
    modified_by = relationship("User", back_populates="modified_documents")


def save_document(filepath, project_id, project_unique_no, revision, modified_by_id, note=None):
    """
    Save a binary document to the database with foreign key constraints.

    Args:
        filepath (str): Path to the file to save.
        project_id (int): FK to projects.id.
        project_unique_no (int): FK to projects.unique_no.
        revision (int): Document revision number.
        modified_by_id (int): FK to users.id (modifier).
        note (str, optional): Additional notes.

    Returns:
        tuple: (success: bool, message: str)
    """
    session = SessionLocal()
    try:
        # Read file as binary
        with open(filepath, 'rb') as f:
            binary_data = f.read()

        # Extract metadata
        filename = os.path.basename(filepath)
        filetype = filename.split('.')[-1].lower()
        modified_at = now_jalali_str()

        # Create new document instance
        doc = Document(
            project_id=project_id,
            project_unique_no=project_unique_no,
            revision=revision,
            filename=filename,
            filetype=filetype,
            data=binary_data,
            modified_by_id=modified_by_id,
            modified_at=modified_at,
            note=note
        )

        session.add(doc)
        session.commit()
        return True, f"Document '{filename}' saved successfully!"
    except Exception as e:
        session.rollback()
        print(traceback.format_exc())
        return False, f"Error saving document: {str(e)}"
    finally:
        session.close()

def retrieve_document(doc_id, output_path):
    """
    Retrieve a document from DB and save to disk.
    """
    session = SessionLocal()
    try:
        doc = session.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return False, f"Document with ID {doc_id} not found."

        with open(output_path, 'wb') as f:
            f.write(doc.data)

        return True, f"Document saved to '{output_path}'"
    except Exception as e:
        print(traceback.format_exc())
        return False, f"Error retrieving document: {str(e)}"
    finally:
        session.close()

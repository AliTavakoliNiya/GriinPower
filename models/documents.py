import os
import traceback

import jdatetime
from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String, Text
from models import Base
from sqlalchemy.orm import relationship

from utils.database import SessionLocal
from sqlalchemy.orm import joinedload


def now_jalali():
    return jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    document_title = Column(String, nullable=False)
    project_code = Column(String, ForeignKey("projects.code"), nullable=False)
    project_unique_no = Column(String, ForeignKey("projects.unique_no"), nullable=True)
    revision = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    modified_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    modified_at = Column(String, nullable=False, default=now_jalali)
    note = Column(Text, nullable=True)

    # Relationships
    modified_by = relationship("User", back_populates="modified_documents")

    def __repr__(self):
        return f"<Document id={self.id} filename='{self.filename}' revision={self.revision}>"


def upload_document(filepath, document_title, project_code, project_unique_no, revision, modified_by_id, note=None):
    """
    Save a binary document to the database with foreign key constraints.

    Args:
        filepath (str): Path to the file to save.
        project_code (str): FK to projects.code.
        project_unique_no (str): FK to projects.unique_no.
        revision (int): Document revision number.
        modified_by_id (int): FK to users.id (modifier).
        note (str, optional): Additional notes.

    Returns:
        tuple: (success: bool, message: str)
        :param document_title:
    """
    session = SessionLocal()
    try:
        # Read file as binary
        with open(filepath, 'rb') as f:
            binary_data = f.read()

        # Extract metadata
        filename = os.path.basename(filepath)
        filetype = filename.split('.')[-1].lower()
        modified_at = now_jalali()

        # Create new document instance
        doc = Document(
            project_code=project_code,
            document_title=document_title,
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


def get_documents(project_code: int, project_unique_no: str = None, document_title: str = ""):
    """Retrieve documents matching project and title filter."""
    Session = SessionLocal()
    try:
        if not document_title.strip():
            return False, "Document title is required.", []

        query = Session.query(Document).options(joinedload(Document.modified_by)).filter(
            Document.project_code == project_code,
            Document.document_title.ilike(f"%{document_title.strip()}%")
        )

        if project_unique_no:
            query = query.filter(Document.project_unique_no == project_unique_no)

        documents = query.all()
        return True, "", documents
    except Exception as e:
        return False, str(e), []
    finally:
        Session.close()

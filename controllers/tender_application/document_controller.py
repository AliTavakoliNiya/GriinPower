import subprocess

from models.documents import get_documents

class DocumentController:
    def __init__(self, view):
        self.view = view

    def load_documents(self, project_code: str, project_unique_no: str = None, document_title: str = ""):
        success, message, documents = get_documents(project_code, project_unique_no, document_title)
        return success, message, documents

    def download_document(self, document, save_path: str):
        try:
            with open(save_path, "wb") as f:
                f.write(document.data)
            try:
                subprocess.Popen(['start', '', save_path], shell=True)
                return "Success", "Successfully saved file"
            except Exception as e:
                return  "Open Error", f"File saved but could not be opened:\n{str(e)}"

        except Exception as e:
            self.view.show_critical("Save Error", str(e))
            return "Open Error", str(e)


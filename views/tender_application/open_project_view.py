from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from models.projects import get_all_project
from models.user_model import get_all_users
from views.message_box_view import show_message


class OpenProjectView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/open_project_view.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")
        self.settings = QSettings("Griin", "GriinPower")

        self.project_code.textChanged.connect(self.code_change)
        self.project_unique_code.currentIndexChanged.connect(self.projec_unique_code_changed)
        self.open_project_btn.clicked.connect(self.open_project_btn_clicked)
        self.new_revision_btn.clicked.connect(self.new_revision_btn_clicked)

        success, self.all_projects = get_all_project()
        success, self.all_users = get_all_users()
        self.clear_form()

        self.show()

    def clear_form(self):
        self.selected_project = None
        self.project_unique_code.clear()
        self.project_name.setText("")
        self.project_code_uniq_code.setText("")
        self.current_revision.setText("")
        self.last_modified_by.setText("")

    def code_change(self):
        entered_code = self.project_code.text().strip()

        if not entered_code:
            self.clear_form()
            return

        # Find all matching projects by code (case-insensitive)
        matches = [
            project for project in self.all_projects
            if (project.code or "").strip().lower() == entered_code.lower()
        ]

        if not matches:
            self.clear_form()
            return

        self.selected_projects = matches

        # Update the QComboBox with unique_no values
        for proj in matches:
            self.project_unique_code.addItem(proj.unique_no)

    def projec_unique_code_changed(self):
        selected_unique_no = self.project_unique_code.currentText().strip()

        if not selected_unique_no:
            self.selected_project = None
            return

        # Find the first matching project with that unique_no
        max_revision = 0
        for project in self.selected_projects:
            if project.unique_no == selected_unique_no:
                if project.revision >= max_revision:
                    max_revision = project.revision
                    self.selected_project = project

        if self.selected_project:
            self.project_name.setText(self.selected_project.name)
            self.project_code_uniq_code.setText(f"{self.selected_project.code} - {self.selected_project.unique_no}")
            self.current_revision.setText(str(self.selected_project.revision).zfill(2))
            for user in self.all_users:
                if user.id == self.selected_project.modified_by_id:
                    full_name = f"{user.first_name} {user.last_name}".title()
                    modified_time = f"{self.selected_project.modified_at}"
                    self.last_modified_by.setText(f"{full_name}\n{modified_time}")
                    break

    def open_project_btn_clicked(self):
        if not self.selected_project:
            show_message("Please select a project before continuing.")
            return

        # dont change id to update result
        self.accept()  # Closes the dialog and sets result to Accepted (True)

    def new_revision_btn_clicked(self):
        if not self.selected_project:
            show_message("Please select a project before continuing.")
            return

        self.selected_project.id = None # to save new project
        self.selected_project.revision += 1
        self.accept()  # Closes the dialog and sets result to Accepted (True)

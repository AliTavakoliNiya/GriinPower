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

        # Load the UI for opening a project
        uic.loadUi("ui/open_project_view.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("GriinPower")

        # App settings
        self.settings = QSettings("Griin", "GriinPower")

        # Connect UI signals to functions
        self.project_code.textChanged.connect(self.code_change)
        self.project_unique_code.currentIndexChanged.connect(self.projec_unique_code_changed)
        self.open_project_btn.clicked.connect(self.open_project_btn_clicked)
        # self.new_revision_btn.clicked.connect(self.new_revision_btn_clicked)  # (If needed)

        # Load data
        success, self.all_projects = get_all_project()
        success, self.all_users = get_all_users()

        # Clear form at start
        self.clear_form()

        # Show dialog
        self.show()

    def clear_form(self):
        """Reset form to initial state."""
        self.selected_project = None
        self.project_unique_code.clear()
        self.project_name.setText("")
        self.project_code_uniq_code.setText("")
        self.current_revision.setText("")
        self.last_modified_by.setText("")

    def code_change(self):
        """Triggered when project code text is changed."""
        entered_code = self.project_code.text().strip()

        if not entered_code:
            self.clear_form()
            return

        # Find all projects matching the entered code (case-insensitive)
        self.selected_projects = [
            project for project in self.all_projects
            if (project.code or "").strip().lower() == entered_code.lower()
        ]

        if not self.selected_projects:
            self.clear_form()
            return

        # Populate unique_no combobox
        self.project_unique_code.clear()
        for proj in self.selected_projects:
            self.project_unique_code.addItem(proj.unique_no)

    def projec_unique_code_changed(self):
        """Triggered when user selects a different unique code."""
        selected_unique_no = self.project_unique_code.currentText().strip()

        if not selected_unique_no:
            self.selected_project = None
            return

        # Pick the highest revision project with the selected unique number
        max_revision = -1
        for project in self.selected_projects:
            if project.unique_no == selected_unique_no and project.revision >= max_revision:
                max_revision = project.revision
                self.selected_project = project

        # Fill form fields with selected project data
        if self.selected_project:
            self.project_name.setText(self.selected_project.name)
            self.project_code_uniq_code.setText(f"{self.selected_project.code} - {self.selected_project.unique_no}")
            self.current_revision.setText(str(self.selected_project.revision).zfill(2))

            # Set last modified user information
            for user in self.all_users:
                if user.id == self.selected_project.modified_by_id:
                    full_name = f"{user.first_name} {user.last_name}".title()
                    modified_time = f"{self.selected_project.modified_at}"
                    self.last_modified_by.setText(f"{full_name}\n{modified_time}")
                    break

    def open_project_btn_clicked(self):
        """Triggered when user clicks 'Open Project' button."""
        if not self.selected_project:
            show_message("Please select a project before continuing.")
            return

        # Accept the dialog (QDialog.Accepted)
        self.accept()


    # def new_revision_btn_clicked(self):
    #     if not self.selected_project:
    #         show_message("Please select a project before continuing.")
    #         return
    #
    #     self.selected_project.id = None # to save new project
    #     self.selected_project.revision += 1
    #     self.accept()  # Closes the dialog and sets result to Accepted (True)

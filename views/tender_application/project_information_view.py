from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from PyQt5 import uic
from PyQt5.QtWidgets import QComboBox, QSpinBox, QCheckBox
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QLineEdit
)
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from controllers.tender_application.project_session_controller import ProjectSession
from controllers.user_session_controller import UserSession
from models.documents import Document
from models.documents import upload_document
from utils.database import SessionLocal
from views.message_box_view import show_message


class ProjectInformationTab(QWidget):
    def __init__(self, main_view):
        super().__init__()
        uic.loadUi("ui/tender_application/project_information_tab.ui", self)
        self.main_view = main_view

        self.current_project = ProjectSession()
        self.current_user = UserSession()
        self.electrical_specs = self.current_project.project_electrical_specs
        self._initialize_info()

        self.upload_technical_data_btn.clicked.connect(self.upload_technical_data)
        self.download_technical_data_btn.clicked.connect(self.download_technical_data)

        if self.current_project.revision != None:
            self.set_project_info_ui_values()

    def _initialize_info(self):
        """ --------------------------- Project Information --------------------------- """
        self.project_name.textChanged.connect(self._handle_project_name_changed)
        self.project_code.textChanged.connect(self._handle_project_code_changed)
        self.project_unique_code.textChanged.connect(self._handle_project_unique_code_changed)
        self.project_site_location.textChanged.connect(self._handle_project_site_location_changed)

        """ --------------------------- Site Condition --------------------------- """
        self.project_m_voltage.currentIndexChanged.connect(self._handle_m_voltage_changed)
        self.project_l_voltage.currentIndexChanged.connect(self._handle_l_voltage_changed)
        self.max_temprature.valueChanged.connect(self._handle_max_temperature_changed)
        self.min_temprature.valueChanged.connect(self._handle_min_temperature_changed)
        self.project_voltage_variation.currentIndexChanged.connect(self._handle_voltage_variation_changed)
        self.altitude_elevation.valueChanged.connect(self._handle_altitude_changed)
        self.humidity.valueChanged.connect(self._handle_humidity_changed)
        self.project_frequency.currentIndexChanged.connect(self._handle_frequency_changed)
        self.project_frequency_variation.currentIndexChanged.connect(self._handle_frequency_variation_changed)

        """ --------------------------- Owner --------------------------- """
        self.owner_name.textChanged.connect(self._handle_owner_changed)
        self.consultant_name.textChanged.connect(self._handle_consultant_name_changed)
        self.employer_name.textChanged.connect(self._handle_employer_name_changed)

        """ --------------------------- Electrical Contact Person --------------------------- """
        self.el_contact_name.textChanged.connect(self._handle_el_contact_name_changed)
        self.el_contact_position.textChanged.connect(self._handle_el_contact_position_changed)
        self.el_contact_phone.textChanged.connect(self._handle_el_contact_phone_changed)

        """ --------------------------- Mechanical Contact Person --------------------------- """
        self.me_contact_name.textChanged.connect(self._handle_me_contact_name_changed)
        self.me_contact_position.textChanged.connect(self._handle_me_contact_position_changed)
        self.me_contact_phone.textChanged.connect(self._handle_me_contact_phone_changed)

        """ --------------------------- Commercial Contact Person --------------------------- """
        self.co_contact_name.textChanged.connect(self._handle_co_contact_name_changed)
        self.co_contact_position.textChanged.connect(self._handle_co_contact_position_changed)
        self.co_contact_phone.textChanged.connect(self._handle_co_contact_phone_changed)

        """ --------------------------- Approve Vendor List --------------------------- """
        self.proj_avl_siemens.stateChanged.connect(self._handle_proj_avl_siemens_changed)
        self.proj_avl_schneider.stateChanged.connect(self._handle_proj_avl_schneider_changed)
        self.proj_avl_hyundai.stateChanged.connect(self._handle_proj_avl_hyundai_changed)

    def _update_project_value(self, path_list, value=None):
        """Update tender_application details dictionary value at the specified path

        Args:
            path_list: List of keys to navigate the nested dictionary
            value: Value to set (if None, gets from sender widget)
        """
        if value is None:
            # Get value from sender
            sender = self.sender()
            if isinstance(sender, QComboBox):
                value = sender.currentText()
            elif isinstance(sender, QSpinBox):
                value = sender.value()
            elif isinstance(sender, QLineEdit):
                value = sender.text()
            elif isinstance(sender, QCheckBox):
                value = sender.isChecked()
            else:
                return

        # Navigate to the right location in the dictionary
        target = self.electrical_specs
        for key in path_list[:-1]:
            target = target[key]

        # Set the value
        target[path_list[-1]] = value

    """ --------------------------- Project Documents --------------------------- """

    def upload_technical_data(self):
        # Open file dialog to select a document
        file_path, _ = QFileDialog.getOpenFileName(None, "Select Document File")
        if file_path:
            # Call save_document with proper arguments
            result, message = upload_document(
                filepath=file_path,
                project_id=self.current_project.id,
                project_unique_no=self.current_project.unique_no,  # new argument
                revision=self.current_project.revision,
                modified_by_id=self.current_user.id,
                note=""  # or get note from user input if you want
            )
            if result:
                show_message("Saved successfully", "Saved")
            else:
                show_message(message, "Error")

    def download_technical_data(self):
        if not hasattr(self, 'document_downloader_view') or self.document_downloader_view is None:
            self.document_downloader_view = DocumentDownloader(self)
        self.document_downloader_view.load_documents(
            project_id=self.current_project.id,
            project_unique_no=self.current_project.unique_no
        )
        self.document_downloader_view.show()

    """ --------------------------- Project Information --------------------------- """

    def _handle_project_name_changed(self):
        self.current_project.name = str(self.project_name.text())

    def _handle_project_code_changed(self):
        self.current_project.code = str(self.project_code.text())

    def _handle_project_unique_code_changed(self):
        self.current_project.unique_no = str(self.project_unique_code.text())

    def _handle_project_site_location_changed(self):
        self._update_project_value(["project_info", "project_site_location"],
                                   str(self.project_site_location.toPlainText()))

    """ --------------------------- Site Condition --------------------------- """

    def _handle_m_voltage_changed(self):
        self._update_project_value(["project_info", "m_voltage"], float(self.project_m_voltage.currentText()) * 1000)

    def _handle_l_voltage_changed(self):
        self._update_project_value(["project_info", "l_voltage"], float(self.project_l_voltage.currentText()))

    def _handle_max_temperature_changed(self, value):
        self._update_project_value(["project_info", "maximum_temprature"], value)

    def _handle_min_temperature_changed(self, value):
        self._update_project_value(["project_info", "minimum_temprature"], value)

    def _handle_voltage_variation_changed(self):
        self._update_project_value(["project_info", "voltage_variation"],
                                   float(self.project_voltage_variation.currentText()))

    def _handle_altitude_changed(self, value):
        self._update_project_value(["project_info", "altitude_elevation"], value)

    def _handle_humidity_changed(self, value):
        self._update_project_value(["project_info", "humidity"], value)

    def _handle_frequency_changed(self):
        self._update_project_value(["project_info", "voltage_frequency"], float(self.project_frequency.currentText()))

    def _handle_frequency_variation_changed(self):
        self._update_project_value(["project_info", "frequency_variation"],
                                   float(self.project_frequency_variation.currentText()))

    """ --------------------------- Electrical Contact Person --------------------------- """

    def _handle_el_contact_name_changed(self):
        self._update_project_value(["project_info", "el_contact_name"], str(self.el_contact_name.text()))

    def _handle_el_contact_position_changed(self):
        self._update_project_value(["project_info", "el_contact_position"], str(self.el_contact_position.text()))

    def _handle_el_contact_phone_changed(self):
        self._update_project_value(["project_info", "el_contact_phone"], str(self.el_contact_phone.text()))

    """ --------------------------- Mechanical Contact Person --------------------------- """

    def _handle_me_contact_name_changed(self):
        self._update_project_value(["project_info", "me_contact_name"], str(self.me_contact_name.text()))

    def _handle_me_contact_position_changed(self):
        self._update_project_value(["project_info", "me_contact_position"], str(self.me_contact_position.text()))

    def _handle_me_contact_phone_changed(self):
        self._update_project_value(["project_info", "me_contact_phone"], str(self.me_contact_phone.text()))

    """ --------------------------- Commercial Contact Person --------------------------- """

    def _handle_co_contact_name_changed(self):
        self._update_project_value(["project_info", "co_contact_name"], str(self.co_contact_name.text()))

    def _handle_co_contact_position_changed(self):
        self._update_project_value(["project_info", "co_contact_position"], str(self.co_contact_position.text()))

    def _handle_co_contact_phone_changed(self):
        self._update_project_value(["project_info", "co_contact_phone"], str(self.co_contact_phone.text()))

    """ --------------------------- Owner --------------------------- """

    def _handle_owner_changed(self):
        self._update_project_value(["project_info", "owner_name"], str(self.owner_name.text()))

    def _handle_consultant_name_changed(self):
        self._update_project_value(["project_info", "consultant_name"], str(self.consultant_name.text()))

    def _handle_employer_name_changed(self):
        self._update_project_value(["project_info", "employer_name"], str(self.employer_name.text()))

    """ --------------------------- Approve Vendor List --------------------------- """

    def _handle_proj_avl_siemens_changed(self):  # value = sender.isChecked()
        if self.proj_avl_siemens.isChecked() and "siemens" not in self.electrical_specs["project_info"]["proj_avl"]:
            self.electrical_specs["project_info"]["proj_avl"].append("siemens")
        elif not self.proj_avl_siemens.isChecked() and "siemens" in self.electrical_specs["project_info"]["proj_avl"]:
            self.electrical_specs["project_info"]["proj_avl"].remove("siemens")

    def _handle_proj_avl_schneider_changed(self):
        if self.proj_avl_schneider.isChecked() and "schneider electric" not in self.electrical_specs["project_info"][
            "proj_avl"]:
            self.electrical_specs["project_info"]["proj_avl"].append("schneider electric")
        elif not self.proj_avl_schneider.isChecked() and "schneider electric" in self.electrical_specs["project_info"][
            "proj_avl"]:
            self.electrical_specs["project_info"]["proj_avl"].remove("schneider electric")

    def _handle_proj_avl_hyundai_changed(self):
        if self.proj_avl_hyundai.isChecked() and "hyundai" not in self.electrical_specs["project_info"]["proj_avl"]:
            self.electrical_specs["project_info"]["proj_avl"].append("hyundai")
        elif not self.proj_avl_hyundai.isChecked() and "hyundai" in self.electrical_specs["project_info"]["proj_avl"]:
            self.electrical_specs["project_info"]["proj_avl"].remove("hyundai")

    def check_info_tab_ui_rules(self):
        if self.project_m_voltage.currentIndex() == 0:
            show_message("Please Choose M Voltage", "Error")
            return False

        if self.project_l_voltage.currentIndex() == 0:
            show_message("Please Choose L Voltage", "Error")
            return False

        return True

    """ Load Pervios Revision as need """

    def set_project_info_ui_values(self):
        """
        Set values for UI elements.
        """
        try:
            # Project Information
            self.project_name.setText(self.current_project.name)
            self.project_code.setText(self.current_project.code)
            self.project_unique_code.setText(self.current_project.unique_no)
            self.project_site_location.setPlainText(self.electrical_specs['project_info']['project_site_location'])

            # Company Information
            self.owner_name.setText(self.electrical_specs['project_info']['owner_name'])
            self.consultant_name.setText(self.electrical_specs['project_info']['consultant_name'])
            self.employer_name.setText(self.electrical_specs['project_info']['employer_name'])

            # Contact Information - Electrical
            self.el_contact_name.setText(self.electrical_specs['project_info']['el_contact_name'])
            self.el_contact_position.setText(self.electrical_specs['project_info']['el_contact_position'])
            self.el_contact_phone.setText(self.electrical_specs['project_info']['el_contact_phone'])

            # Contact Information - Mechanical
            self.me_contact_name.setText(self.electrical_specs['project_info']['me_contact_name'])
            self.me_contact_position.setText(self.electrical_specs['project_info']['me_contact_position'])
            self.me_contact_phone.setText(self.electrical_specs['project_info']['me_contact_phone'])

            # Contact Information - Construction
            self.co_contact_name.setText(self.electrical_specs['project_info']['co_contact_name'])
            self.co_contact_position.setText(self.electrical_specs['project_info']['co_contact_position'])
            self.co_contact_phone.setText(self.electrical_specs['project_info']['co_contact_phone'])

            # Electrical Specifications - Voltage
            self.project_m_voltage.setCurrentText(str(self.electrical_specs['project_info']['m_voltage'] / 1000))
            self.project_l_voltage.setCurrentText(str(int(self.electrical_specs['project_info']['l_voltage'])))
            self.project_voltage_variation.setCurrentText(
                str(int(self.electrical_specs['project_info']['voltage_variation'])))

            # Electrical Specifications - Frequency
            self.project_frequency.setCurrentText(str(int(self.electrical_specs['project_info']['voltage_frequency'])))
            self.project_frequency_variation.setCurrentText(
                str(int(self.electrical_specs['project_info']['frequency_variation'])))

            # Environmental Conditions
            self.min_temprature.setValue(self.electrical_specs['project_info']['minimum_temprature'])
            self.max_temprature.setValue(self.electrical_specs['project_info']['maximum_temprature'])
            self.humidity.setValue(self.electrical_specs['project_info']['humidity'])
            self.altitude_elevation.setValue(self.electrical_specs['project_info']['altitude_elevation'])

            # Available Equipment Checkboxes
            self.proj_avl_schneider.setChecked(
                'schneider electric' in self.electrical_specs['project_info']['proj_avl'])
            self.proj_avl_hyundai.setChecked('hyundai' in self.electrical_specs['project_info']['proj_avl'])
            self.proj_avl_siemens.setChecked('siemens' in self.electrical_specs['project_info']['proj_avl'])
        except KeyError as e:
            show_message(f"KeyError: Missing key in electrical_specs: {e}")
        except AttributeError as e:
            show_message(f"AttributeError: UI element not found: {e}")
        except Exception as e:
            show_message(f"Unexpected error: {e}")


class DocumentDownloader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Document Downloader")
        self.setGeometry(200, 200, 800, 400)

        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Filetype", "Revision", "Size", "Modified By", "Modified At", "Note"
        ])
        self.table.setSelectionBehavior(self.table.SelectRows)

        self.download_button = QPushButton("Download Selected")
        self.download_button.clicked.connect(self.download_document)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.download_button)
        self.setLayout(self.layout)

        self.documents = []

    def load_documents(self, project_id: int, project_unique_no: str = None):
        """Load documents for a given project_id and optional unique_no."""
        self.documents.clear()
        self.table.setRowCount(0)

        session: Session = SessionLocal()
        try:
            query = session.query(Document).options(joinedload(Document.modified_by)).filter(
                Document.project_id == project_id
            )
            if project_unique_no:
                query = query.filter(Document.project_unique_no == project_unique_no)

            self.documents = query.all()
            self.table.setRowCount(len(self.documents))

            for row, doc in enumerate(self.documents):
                modified_by_name = (
                    f"{doc.modified_by.first_name} {doc.modified_by.last_name}".title()
                    if doc.modified_by else "Unknown"
                )

                if doc.data:
                    size_bytes = len(doc.data)
                    if size_bytes >= 1024 * 1024:
                        size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                    else:
                        size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = "0 KB"

                items = [
                    QTableWidgetItem(doc.filename),
                    QTableWidgetItem(doc.filetype),
                    QTableWidgetItem(str(doc.revision)),
                    QTableWidgetItem(size_str),
                    QTableWidgetItem(modified_by_name),
                    QTableWidgetItem(doc.modified_at),
                    QTableWidgetItem(doc.note or "")
                ]

                for col, item in enumerate(items):
                    item.setForeground(QColor("black"))
                    self.table.setItem(row, col, item)

            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
        finally:
            session.close()

    def download_document(self):
        selected = self.table.currentRow()
        if selected < 0 or selected >= len(self.documents):
            QMessageBox.warning(self, "No Selection", "Please select a document to download.")
            return

        doc = self.documents[selected]
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", doc.filename)

        if save_path:
            try:
                with open(save_path, "wb") as f:
                    f.write(doc.data)
                QMessageBox.information(self, "Success", f"File saved to:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))

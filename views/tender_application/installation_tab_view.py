from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from controllers.tender_application.installation_controller import InstallationController
from controllers.tender_application.project_session_controller import ProjectSession
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QTableView
from utils.pandas_model import PandasModel
from views.message_box_view import show_message


class InstallationTab(QWidget):
    def __init__(self, main_view):
        super().__init__()
        uic.loadUi("ui/tender_application/installation_tab.ui", self)
        self.main_view = main_view

        self.current_project = ProjectSession()
        self.electrical_specs = self.current_project.project_electrical_specs

        self.width_field.valueChanged.connect(self.width_field_value_handler)
        self.height_field.valueChanged.connect(self.height_field_value_handler)
        self.depth_field.valueChanged.connect(self.depth_field_value_handler)
        self.ccr_distance.valueChanged.connect(self.ccr_field_value_handler)

        self.update_table.clicked.connect(self.generate_result)
        self.set_installation_ui_values()

    def depth_field_value_handler(self):
        self.electrical_specs["installation"]["depth"] = self.depth_field.value()

    def width_field_value_handler(self):
        self.electrical_specs["installation"]["width"] = self.width_field.value()

    def height_field_value_handler(self):
        self.electrical_specs["installation"]["height"] = self.height_field.value()

    def ccr_field_value_handler(self):
        self.electrical_specs["installation"]["ccr"] = self.ccr_distance.value()

    def _setup_result_table(self):
        self.installation_panel.setAlternatingRowColors(True)
        self.installation_panel.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.installation_panel.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.installation_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.installation_panel.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.installation_panel.setWordWrap(True)
        self.installation_panel.setTextElideMode(Qt.ElideRight)
        self.installation_panel.verticalHeader().setVisible(False)

    def generate_result(self):
        installation_controller = InstallationController()
        self.installation_panel = installation_controller.build_panel()

        df = pd.DataFrame(self.installation_panel)
        df = self._add_summary_row(df)
        model = PandasModel(df)
        self.installation_table.setModel(model)

        self._resize_columns_to_contents(model, self.installation_table)

        header = self.installation_table.horizontalHeader()
        for col in range(model.columnCount(None) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(model.columnCount(None) - 1, QHeaderView.Stretch)

        self.installation_table.resizeRowsToContents()
        self.installation_table.setColumnHidden(2, True)  # hide order_number column

    def _add_summary_row(self, df):
        summary = {
            col: df[col].sum() if col == "total_price" else ("Total" if col.lower() == "type" else "")
            for col in df.columns
        }
        return pd.concat([df, pd.DataFrame([summary], index=["Total"])])

    def _resize_columns_to_contents(self, model, table):
        metrics = table.fontMetrics()

        for col in range(model.columnCount(None)):
            max_width = metrics.horizontalAdvance(str(model.headerData(col, Qt.Horizontal, Qt.DisplayRole))) + 20
            for row in range(model.rowCount(None)):
                index = model.index(row, col)
                text = str(model.data(index, Qt.DisplayRole))
                max_width = max(max_width, metrics.horizontalAdvance(text) + 20)
            table.setColumnWidth(col, max_width)

    """ Load Pervios Revision as need """

    def set_installation_ui_values(self):  # Using for open pervios project
        """
        Set values for UI elements based on the self.electrical_specs dictionary.
        """
        new_proj = True if self.current_project.revision == None else False
        try:
            # QLabel elements
            self.height_field.setValue(float(self.electrical_specs['installation']['height']))
            self.width_field.setValue(float(self.electrical_specs['installation']['width']))
            self.depth_field.setValue(float(self.electrical_specs['installation']['depth']))
            self.ccr_distance.setValue(float(self.electrical_specs['installation']['ccr']))
        except KeyError as e:
            show_message(f"KeyError: Missing key in electrical_specs: {e}")
        except AttributeError as e:
            show_message(f"AttributeError: UI element not found: {e}")
        except Exception as e:
            show_message(f"Unexpected error: {e}")

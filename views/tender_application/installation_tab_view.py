from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from controllers.tender_application.installation_controller import InstallationController
from controllers.tender_application.project_session_controller import ProjectSession
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QTableView

from controllers.tender_application.panel_controller import PanelController
from models.items.electrical_panel import get_electrical_panel_by_spec
from utils.pandas_model import PandasModel


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
        self.ccr_field.valueChanged.connect(self.ccr_field_value_handler)

        self.update_table.clicked.connect(self.generate_result)



    def depth_field_value_handler(self):
        self.electrical_specs["installation"]["depth"] = self.depth_field.value()

    def width_field_value_handler(self):
        self.electrical_specs["installation"]["width"] = self.width_field.value()

    def height_field_value_handler(self):
        self.electrical_specs["installation"]["height"] = self.height_field.value()

    def ccr_field_value_handler(self):
        self.electrical_specs["installation"]["ccr"] = self.ccr_field.value()

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
        self.installation_panel_table.setModel(model)

        self._resize_columns_to_contents(model, self.installation_panel_table)

        header = self.installation_panel_table.horizontalHeader()
        for col in range(model.columnCount(None) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(model.columnCount(None) - 1, QHeaderView.Stretch)

        self.installation_panel_table.resizeRowsToContents()

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

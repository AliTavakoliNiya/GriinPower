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

        self.update_table.clicked.connect(self.generate_result)

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



import openpyxl
import pandas as pd
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTreeWidget, QTreeWidgetItem,
    QPushButton, QVBoxLayout, QFileDialog
)
from PyQt5.QtWidgets import QTableView, QHeaderView
from openpyxl.styles import Font, PatternFill

from controllers.tender_application.bagfilter_controller import BagfilterController
from controllers.tender_application.electric_motor_controller import ElectricMotorController
from controllers.tender_application.fan_damper_controller import FanDamperController
from controllers.tender_application.fresh_air_controller import FreshAirController
from controllers.tender_application.hopper_heater_controller import HopperHeaterController
from controllers.tender_application.project_session_controller import ProjectSession
from controllers.tender_application.transport_controller import TransportController
from controllers.tender_application.vibration_controller import VibrationController
from utils.pandas_model import PandasModel
from models import projects
from views.message_box_view import show_message, confirmation


class ResultTab(QWidget):
    def __init__(self, main_view):
        super().__init__()
        uic.loadUi("ui/tender_application/results_tab.ui", self)

        self.main_view = main_view
        self.electrical_specs = ProjectSession().project_electrical_specs
        self.tabWidget.setCurrentIndex(0)

        self.tables = {
            "bagfilter_panel_table": self.bagfilter_panel_table,
            "fan_damper_panel_table": self.fan_damper_panel_table,
            "transport_panel_table": self.transport_panel_table,
            "fresh_air_panel_table": self.fresh_air_panel_table,
            "vibration_panel_table": self.vibration_panel_table,
            "hopper_heater_panel_table": self.hopper_heater_panel_table,
            "summary_panel_table": self.summary_panel_table
        }

        self.panels = {}

        self._setup_result_table()

        self.excel_btn.clicked.connect(self._export_to_excel)
        self.show_datail_btn.clicked.connect(self.show_datail_btn_handler)
        self.save_changes_btn.clicked.connect(self.save_changes_btn_handler)

        self.update_table.clicked.connect(self.generate_panels)

    def save_changes_btn_handler(self):
        if not confirmation(f"You are about to save changes, Are you sure?"):
            return

        current_project = ProjectSession()
        success, msg = projects.save_project(current_project)
        if success:
            show_message(msg, title="Saved")
            self.main_view.close()
        else:
            show_message(msg, title="Error")

    def _setup_result_table(self):
        for table in self.tables.values():
            table.setAlternatingRowColors(True)
            table.setHorizontalScrollMode(QTableView.ScrollPerPixel)
            table.setVerticalScrollMode(QTableView.ScrollPerPixel)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            table.setWordWrap(True)
            table.setTextElideMode(Qt.ElideRight)
            table.verticalHeader().setVisible(False)

    def generate_panels(self):

        bagfilter_controller = BagfilterController()
        self.panels["bagfilter_panel"] = bagfilter_controller.build_panel()
        fan_damper_controller = FanDamperController()
        self.panels["fan_damper_panel"] = fan_damper_controller.build_panel()
        transport_controller = TransportController()
        self.panels["transport_panel"] = transport_controller.build_panel()
        fresh_air_controller = FreshAirController()
        self.panels["fresh_air_panel"] = fresh_air_controller.build_panel()
        vibration_controller = VibrationController()
        self.panels["vibration_panel"] = vibration_controller.build_panel()
        hopper_heater_controller = HopperHeaterController()
        self.panels["hopper_heater_panel"] = hopper_heater_controller.build_panel()
        if self.main_view.electrical_tab.fan_checkbox.isChecked():
            electric_motor_controller = ElectricMotorController()
            electric_motor_price_and_effective_date = electric_motor_controller.calculate_price()

        self.generate_table(self.panels["bagfilter_panel"], self.tables["bagfilter_panel_table"])
        self.generate_table(self.panels["fan_damper_panel"], self.tables["fan_damper_panel_table"])
        self.generate_table(self.panels["transport_panel"], self.tables["transport_panel_table"])
        self.generate_table(self.panels["fresh_air_panel"], self.tables["fresh_air_panel_table"])
        self.generate_table(self.panels["vibration_panel"], self.tables["vibration_panel_table"])
        self.generate_table(self.panels["hopper_heater_panel"], self.tables["hopper_heater_panel_table"])
        if self.main_view.electrical_tab.fan_checkbox.isChecked():
            summary_data = self.generate_summary_panel(electric_motor_price_and_effective_date)
        else:
            summary_data = self.generate_summary_panel()
        self.generate_table(summary_data, self.tables["summary_panel_table"])

    def generate_table(self, panel, table):
        df = pd.DataFrame(panel)
        df = self._add_summary_row(df)
        model = PandasModel(df)
        table.setModel(model)

        self._resize_columns_to_contents(model, table)

        header = table.horizontalHeader()
        for col in range(model.columnCount(None) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(model.columnCount(None) - 1, QHeaderView.Stretch)

        table.resizeRowsToContents()

    def _resize_columns_to_contents(self, model, table):
        metrics = table.fontMetrics()

        for col in range(model.columnCount(None)):
            max_width = metrics.horizontalAdvance(str(model.headerData(col, Qt.Horizontal, Qt.DisplayRole))) + 20
            for row in range(model.rowCount(None)):
                index = model.index(row, col)
                text = str(model.data(index, Qt.DisplayRole))
                max_width = max(max_width, metrics.horizontalAdvance(text) + 20)
            table.setColumnWidth(col, max_width)

    def _add_summary_row(self, df):
        summary = {
            col: df[col].sum() if col == "total_price" else ("Total" if col.lower() == "type" else "")
            for col in df.columns
        }
        return pd.concat([df, pd.DataFrame([summary], index=["Total"])])

    def generate_summary_panel(self, electric_motor_price_and_effective_date=None):
        summary = {
            "title": [],
            "Price": [],
            "Note": []
        }

        total_sum = 0

        for name, panel in self.panels.items():
            summary["title"].append(name.replace("_", " ").title())
            panel_df = pd.DataFrame(panel)
            panel_total = panel_df["total_price"].sum() if "total_price" in panel_df.columns else 0
            summary["Price"].append(panel_total)
            summary["Note"].append("")
            total_sum += panel_total

        if self.electrical_specs["fan"]["status"]:
            summary["title"].append("ELECTRIC MOTOR")
            motor_price = electric_motor_price_and_effective_date[0]
            total_sum += motor_price
            summary["Price"].append(motor_price)
            summary["Note"].append(electric_motor_price_and_effective_date[1])

        summary["title"].append("Total")
        summary["Price"].append(total_sum)
        summary["Note"].append("")

        return summary

    def _export_to_excel(self):

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "ReportByGriinPower",
                                                   "Excel Files (*.xlsx)")
        if not file_path:
            return

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for name, table in self.tables.items():
                model = table.model()
                if model is None:
                    continue

                df = model._data.copy()
                df.index = range(1, len(df) + 1)

                df.to_excel(writer, sheet_name=name, index=True, startrow=1)

                workbook = writer.book
                worksheet = writer.sheets[name]

                # Styles
                header_font = Font(bold=True, color="FFFFFF")
                thin_border = openpyxl.styles.Border(
                    left=openpyxl.styles.Side(style='thin'),
                    right=openpyxl.styles.Side(style='thin'),
                    top=openpyxl.styles.Side(style='thin'),
                    bottom=openpyxl.styles.Side(style='thin')
                )
                center_alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center", wrap_text=True)
                header_fill = PatternFill(start_color="FF4F81BD", end_color="FF4F81BD", fill_type="solid")
                zebra_fill = PatternFill(start_color="FFF2F2F2", end_color="FFF2F2F2", fill_type="solid")
                total_fill = PatternFill(start_color="FFFFAA00", end_color="FFFFAA00", fill_type="solid")

                columns = list(df.columns.insert(0, df.index.name or ""))  # Including index

                # Format headers
                for col_idx, col_name in enumerate(columns, 1):
                    cell = worksheet.cell(row=2, column=col_idx)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = center_alignment
                    cell.border = thin_border

                # Format data rows
                for row in worksheet.iter_rows(min_row=3, max_row=worksheet.max_row, max_col=worksheet.max_column):
                    row_idx = row[0].row
                    for col_idx, cell in enumerate(row, 0):
                        cell.alignment = center_alignment
                        cell.border = thin_border

                        col_name = columns[col_idx]
                        if col_name.lower() in ("price", "total_price") and isinstance(cell.value, (int, float)):
                            cell.number_format = '#,##0.00'

                    if row_idx % 2 == 1:
                        for cell in row:
                            cell.fill = zebra_fill

                # Special styling for Total row
                total_row = worksheet.max_row
                for cell in worksheet[total_row]:
                    cell.fill = total_fill

                # Auto-fit column widths
                for column_cells in worksheet.columns:
                    max_length = 0
                    column = column_cells[0].column_letter
                    for cell in column_cells:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    worksheet.column_dimensions[column].width = max(max_length + 2, 10)

                # Freeze header row
                worksheet.freeze_panes = worksheet["A3"]

    def show_datail_btn_handler(self):
        self.show_datail_window = DictionaryViewer(data=self.electrical_specs, parent=self.main_view)


class DictionaryViewer(QMainWindow):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details Viewer")
        self.resize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Panels", "Value"])
        self.tree.setColumnWidth(0, 300)
        self.populate_tree(self.tree.invisibleRootItem(), data)

        # Buttons
        self.print_button = QPushButton("Print to PDF")
        self.print_button.clicked.connect(self.print_to_pdf)

        self.toggle_button = QPushButton("Expand All")
        self.toggle_button.clicked.connect(self.toggle_tree)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.print_button)
        central_widget.setLayout(layout)

        # State tracker
        self.tree_expanded = False

        self.show()

    def toggle_tree(self):
        if self.tree_expanded:
            self.tree.collapseAll()
            self.toggle_button.setText("Expand All")
        else:
            self.tree.expandAll()
            self.toggle_button.setText("Collapse All")
        self.tree_expanded = not self.tree_expanded

    def populate_tree(self, parent_item, dictionary):
        def format_key(key):
            return ' '.join(word.title() for word in str(key).split('_'))

        for key, value in dictionary.items():
            display_key = format_key(key)
            if isinstance(value, dict):
                item = QTreeWidgetItem([display_key])
                parent_item.addChild(item)
                self.populate_tree(item, value)
            else:
                item = QTreeWidgetItem([display_key, str(value)])
                parent_item.addChild(item)

    def print_to_pdf(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)", options=options)
        if filename:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)

            self.tree.expandAll()
            self.tree.resizeColumnToContents(0)
            self.tree.resizeColumnToContents(1)

            # Save original size
            original_size = self.tree.size()

            # Estimate total size
            total_height = self.tree.header().height()
            for i in range(self.tree.topLevelItemCount()):
                total_height += self.tree.sizeHintForRow(0) * (1 + self.count_all_items(self.tree.topLevelItem(i)))

            total_width = sum([self.tree.sizeHintForColumn(i) for i in range(self.tree.columnCount())]) + 20

            # Temporarily resize tree to fit all contents
            self.tree.resize(total_width, total_height)

            painter = QPainter(printer)

            # Calculate scaling
            page_rect = printer.pageRect()
            widget_rect = self.tree.rect()

            margin = 50
            scale_x = (page_rect.width() - 2 * margin) / widget_rect.width()
            scale_y = (page_rect.height() - 2 * margin) / widget_rect.height()
            scale = min(scale_x, scale_y)

            painter.translate(page_rect.left() + margin, page_rect.top() + margin)
            painter.scale(scale, scale)

            # Render the tree
            self.tree.render(painter)

            # Add grid lines
            pen = painter.pen()
            pen.setWidth(1)
            painter.setPen(pen)

            row_height = self.tree.sizeHintForRow(0)
            header_height = self.tree.header().height()
            num_rows = self.count_all_items(self.tree.invisibleRootItem())

            # Horizontal grid lines
            for row in range(num_rows + 2):
                y = header_height + row * row_height
                painter.drawLine(0, y, widget_rect.width(), y)

            # Vertical grid lines
            x = 0
            for col in range(self.tree.columnCount()):
                col_width = self.tree.columnWidth(col)
                x += col_width
                painter.drawLine(x, 0, x, widget_rect.height())

            painter.end()

            # Restore original size
            self.tree.resize(original_size)

    def count_all_items(self, parent_item):
        count = 0
        for i in range(parent_item.childCount()):
            count += 1
            count += self.count_all_items(parent_item.child(i))
        return count

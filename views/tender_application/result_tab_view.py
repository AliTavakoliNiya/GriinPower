import copy
import subprocess

import jdatetime
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
        self.current_project = ProjectSession()
        self.electrical_specs = self.current_project.project_electrical_specs
        self.tabWidget.setCurrentIndex(0)

        self.tables = {
            "bagfilter_table": self.bagfilter_table,
            "fan_damper_table": self.fan_damper_table,
            "transport_table": self.transport_table,
            "fresh_air_table": self.fresh_air_table,
            "vibration_table": self.vibration_table,
            "hopper_heater_table": self.hopper_heater_table,
            "summary_table": self.summary_table
        }

        self.panels = {}

        self._setup_result_table()

        self.excel_btn.clicked.connect(self._export_to_excel)
        self.show_datail_btn.clicked.connect(self.show_datail_btn_handler)
        self.save_changes_btn.clicked.connect(self.save_changes_btn_handler)

        self.update_table.clicked.connect(self.generate_panels)

    def show_datail_btn_handler(self):
        self.show_datail_window = DictionaryTreeViewer(data=self.electrical_specs, parent=self.main_view)

    def save_changes_btn_handler(self):
        if not confirmation(f"You are about to save changes, Are you sure?"):
            return

        current_project = ProjectSession()
        success, msg = projects.save_project(current_project)
        if success:
            show_message(msg, title="Saved")
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

        self.generate_table(panel=self.panels["bagfilter_panel"], table=self.tables["bagfilter_table"])
        self.generate_table(panel=self.panels["fan_damper_panel"], table=self.tables["fan_damper_table"])
        self.generate_table(panel=self.panels["transport_panel"], table=self.tables["transport_table"])
        self.generate_table(panel=self.panels["fresh_air_panel"], table=self.tables["fresh_air_table"])
        self.generate_table(panel=self.panels["vibration_panel"], table=self.tables["vibration_table"])
        self.generate_table(panel=self.panels["hopper_heater_panel"], table=self.tables["hopper_heater_table"])

        panels = copy.deepcopy(self.panels)
        panels["installation_panel"] = self.main_view.installation_tab.installation_panel
        if self.main_view.electrical_tab.fan_checkbox.isChecked():
            summary_data = self._generate_summary_table(
                electric_motor_price_and_effective_date=electric_motor_price_and_effective_date, panels=panels)
        else:
            summary_data = self._generate_summary_table(panels=panels)
        self.generate_table(panel=summary_data, table=self.tables["summary_table"])

    def _add_summary_row(self, df):
        summary = {
            col: df[col].sum() if col == "total_price" else ("Total" if col.lower() == "type" else "")
            for col in df.columns
        }
        return pd.concat([df, pd.DataFrame([summary], index=["Total"])])

    def generate_table(self, panel, table):
        df = pd.DataFrame(panel)
        df = self._add_summary_row(df)
        model = PandasModel(df)
        table.setModel(model)
        # if 'total_price' in df.columns and df.iloc[-1]['total_price'] == 0: # hide 0 price tabs
        #     tab_name = f"self.{table.objectName().replace('table', 'tab')}.hide()"
        #     eval(tab_name)

        header = table.horizontalHeader()
        for col in range(model.columnCount(None) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(model.columnCount(None) - 1, QHeaderView.Stretch)

        self._resize_columns_to_contents(model, table)
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

    def _generate_summary_table(self, panels, electric_motor_price_and_effective_date=None):
        summary = {
            "Title": [],
            "Price": [],
            "Note": []
        }

        total_sum = 0

        for name, panel in panels.items():
            summary["Title"].append(name.replace("_", " ").title())
            panel_df = pd.DataFrame(panel)
            panel_total = panel_df["total_price"].sum() if "total_price" in panel_df.columns else 0
            summary["Price"].append(panel_total)
            summary["Note"].append("")
            total_sum += panel_total

        if self.electrical_specs["fan"]["status"]:
            summary["Title"].append("Electric Motor")
            motor_price = electric_motor_price_and_effective_date[0]
            total_sum += motor_price
            summary["Price"].append(motor_price)
            summary["Note"].append(electric_motor_price_and_effective_date[1])

        summary["Title"].append("Total")
        summary["Price"].append(total_sum)
        summary["Note"].append("")

        return summary

    def _export_to_excel(self):

        tables = {name: table for name, table in self.tables.items()}
        tables["installation_table"] = self.main_view.installation_tab.installation_table

        file_name = f"{self.current_project.name}-{self.current_project.code}-{self.current_project.unique_no}-Rev{str(self.current_project.revision).zfill(2)}"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", file_name, "Excel Files (*.xlsx)")
        if not file_path:
            return

        try:
            report_path = file_path.replace(".xlsx", "(ReportByGriinPower).xlsx")

            self._export_report_excel(tables=tables, file_path=report_path)

            subprocess.Popen(['start', '', report_path], shell=True)

        except Exception as e:
            show_message(message=str(e), title="Error")

    def _export_report_excel(self, tables, file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Export main report sheets
            for name, table in tables.items():
                model = table.model()
                if model is None:
                    continue

                df = model._data.copy()
                df.index = range(1, len(df) + 1)

                df.to_excel(writer, sheet_name=name, index=True, startrow=1)
                self._style_excel_sheet(writer, name)

            # Append factor sheets
            instrument_df, summary_df = self._prepare_factor_data(tables)

            instrument_df.index = range(1, len(instrument_df) + 1)
            instrument_df.to_excel(writer, sheet_name="اقلام ابزار دقیق", startrow=1, index=True)
            self._style_excel_sheet(writer, "اقلام ابزار دقیق")

            summary_df.index = range(1, len(summary_df) + 1)
            summary_df.to_excel(writer, sheet_name="قیمت نهایی", startrow=1, index=True)
            self._style_excel_sheet(writer, "قیمت نهایی")

    def _prepare_factor_data(self, tables):
        instruments_list = [
            'Delta Pressure Transmitter', 'Delta Pressure Switch', 'Pressure Transmitter',
            'Pressure Switch', 'Pressure Gauge', 'Temperature Transmitter', 'Proximity Switch',
            'Vibration Transmitter', 'Speed Detector', 'Level Switch', 'Level Transmitter',
            'Ways Manifold', 'Calibration'
        ]

        bagfilter_price = 0
        instruments_price = 0
        instrument_items = []

        for name, table in tables.items():
            model = table.model()
            if model is None or name in ["summary_table", "installation_table"]:
                continue

            df = model._data.copy()
            df.columns = df.columns.str.lower()  # normalize column names

            for _, row in df.iterrows():
                if "total" in row["type"].lower():
                    continue

                if any(inst in row["type"] for inst in instruments_list):
                    instruments_price += row['total_price']
                    instrument_items.append({
                        "شرح": row["type"],
                        "برند": row.get("brand", ""),
                        "تعداد": row.get("quantity", 1),
                        "قیمت واحد": row.get("price", 0),
                        "قیمت کل": row.get("total_price", 0),
                    })

            bagfilter_price += df.iloc[-1]['total_price']

        bagfilter_price -= instruments_price
        el_motor_price = tables['summary_table'].model()._data.iloc[7]['Price']

        summary_data = [
            [0, 0, 0, bagfilter_price, bagfilter_price, 1, "تابلوبگ فیلتر", 1],
            [0, 0, 0, instruments_price, instruments_price, 1, "ابزار دقیق", 2],
            [0, 0, 0, 3700564000, 0, 1, "کابل", 3],
            [0, 0, 0, 3700564000, 0, 1, "راه اندازی FAT", 4],
            [0, 0, 0, el_motor_price, el_motor_price, 1,
             f" الکتروموتور {int(self.electrical_specs['fan']['motors']['fan']['power'] / 1000)}KW "
             f"{self.electrical_specs['fan']['motors']['fan']['brand']} "
             f"{self.electrical_specs['fan']['motors']['fan']['efficiency_class']}", 5]
        ]

        summary_df = pd.DataFrame(summary_data,
                                  columns=["خرید", "مهندسی", "ساخت", "قیمت کل(ریال)", "قیمت", "تعداد", "شرح", "ردیف"])
        summary_totals = summary_df[["خرید", "مهندسی", "ساخت", "قیمت کل(ریال)", "قیمت"]].sum().to_dict()
        summary_df.loc[len(summary_df)] = {**summary_totals, "تعداد": "", "شرح": "جمع کل", "ردیف": ""}

        instrument_df = pd.DataFrame(instrument_items)
        if not instrument_df.empty:
            total_price = instrument_df["قیمت کل"].sum()
            instrument_df.loc[len(instrument_df)] = {
                "شرح": "جمع کل", "برند": "", "تعداد": "", "قیمت واحد": "", "قیمت کل": total_price
            }

        return instrument_df, summary_df

    def _style_excel_sheet(self, writer, sheet_name):
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        worksheet = writer.sheets[sheet_name]
        max_row = worksheet.max_row
        max_col = worksheet.max_column

        # === Styles ===
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="FF4F81BD", end_color="FF4F81BD", fill_type="solid")
        zebra_fill = PatternFill(start_color="FFF2F2F2", end_color="FFF2F2F2", fill_type="solid")
        total_fill = PatternFill(start_color="FFFFAA00", end_color="FFFFAA00", fill_type="solid")
        alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # === Apply to header row ===
        for col_idx in range(1, max_col + 1):
            cell = worksheet.cell(row=2, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = alignment
            cell.border = thin_border

        # === Apply to data rows ===
        for row in worksheet.iter_rows(min_row=3, max_row=max_row, max_col=max_col):
            for cell in row:
                cell.alignment = alignment
                cell.border = thin_border

                # Price formatting
                if isinstance(cell.value, (int, float)) and cell.column_letter in ['D', 'E', 'F', 'G']:
                    cell.number_format = '#,##0'

            if row[0].row % 2 == 1:
                for cell in row:
                    cell.fill = zebra_fill

        # === Total row formatting ===
        for cell in worksheet[max_row]:
            if isinstance(cell.value, str) and "جمع کل" in cell.value:
                for c in worksheet[max_row]:
                    c.fill = total_fill

        # === Auto column widths ===
        for column_cells in worksheet.columns:
            max_length = max((len(str(cell.value)) for cell in column_cells if cell.value), default=0)
            column_letter = column_cells[0].column_letter
            worksheet.column_dimensions[column_letter].width = max(max_length + 2, 10)

        # === Freeze header ===
        worksheet.freeze_panes = worksheet["A3"]


class DictionaryTreeViewer(QMainWindow):
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

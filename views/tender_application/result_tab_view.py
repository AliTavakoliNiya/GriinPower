import copy
import subprocess
import sys

import pandas as pd
from PyQt5 import uic
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import (QComboBox, QFileDialog, QHeaderView, QMainWindow, QPushButton, QStyledItemDelegate,
                             QTableView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from controllers.tender_application.bagfilter_controller import BagfilterController
from controllers.tender_application.cable_controller import CableController
from controllers.tender_application.electric_motor_controller import ElectricMotorController
from controllers.tender_application.fan_damper_controller import FanDamperController
from controllers.tender_application.fresh_air_controller import FreshAirController
from controllers.tender_application.hopper_heater_controller import HopperHeaterController
from controllers.tender_application.project_session_controller import ProjectSession
from controllers.tender_application.transport_controller import TransportController
from controllers.tender_application.vibration_controller import VibrationController
from utils.pandas_model import PandasModel
from views.message_box_view import show_message




class ResultTab(QWidget):
    def __init__(self, main_view):
        super().__init__()
        uic.loadUi("ui/tender_application/results_tab.ui", self)

        self.main_view = main_view
        self.current_project = ProjectSession()
        self.electrical_specs = self.current_project.project_electrical_specs

        self._init_tables()
        self._init_tabs()
        self._style_all_tables()

        self.excel_btn.clicked.connect(self._export_to_excel)
        self.show_datail_btn.clicked.connect(self._show_detail)
        self.update_table.clicked.connect(self.generate_data)

    def _init_tables(self):
        self.tables = {
            "bagfilter_table": self.bagfilter_table,
            "fan_damper_table": self.fan_damper_table,
            "transport_table": self.transport_table,
            "fresh_air_table": self.fresh_air_table,
            "vibration_table": self.vibration_table,
            "hopper_heater_table": self.hopper_heater_table,
            "cable_table": self.cable_table,
            "summary_table": self.summary_table
        }

    def _init_tabs(self):
        self.all_tabs = [
            ("bagfilter_table", self.bagfilter_tab, "Bagfilter"),
            ("fan_damper_table", self.fan_damper_tab, "Fan Damper"),
            ("transport_table", self.transport_tab, "Transport"),
            ("fresh_air_table", self.fresh_air_tab, "Fresh Air"),
            ("vibration_table", self.vibration_tab, "Vibration"),
            ("hopper_heater_table", self.hopper_heater_tab, "Hopper Heater"),
            ("cable_table", self.cable_tab, "Cable"),
            ("summary_table", self.summary_tab, "Summary")
        ]

    def _style_all_tables(self):
        for table in self.tables.values():
            self._style_table(table)

    def _style_table(self, table: QTableView):
        table.setAlternatingRowColors(True)
        table.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        table.setVerticalScrollMode(QTableView.ScrollPerPixel)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setWordWrap(True)
        table.setTextElideMode(Qt.ElideRight)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(True)

    def _show_detail(self):
        viewer = DictionaryTreeViewer(data=self.electrical_specs, parent=self.main_view)
        viewer.show()

    def generate_data(self):
        self.panels = self._build_all_panels()
        for key, panel in self.panels.items():
            table_name = key.replace("_panel", "_table")
            if table_name in self.tables:
                self._populate_table_view(panel, self.tables[table_name])

        panels_copy = copy.deepcopy(self.panels)
        panels_copy["installation_panel"] = self.main_view.installation_tab.installation_panel

        if self.main_view.electrical_tab.fan_checkbox.isChecked():
            motor_ctrl = ElectricMotorController()
            motor_info = motor_ctrl.calculate_price()
            summary_data = self._generate_summary_data(panels_copy, motor_info)
            self._set_summary_model(summary_data, use_brands=True)
        else:
            summary_data = self._generate_summary_data(panels_copy)
            self._populate_table_view(summary_data, self.tables["summary_table"])

        self._refresh_tabs()

    def _build_all_panels(self):
        controllers = {
            "bagfilter_panel": BagfilterController,
            "fan_damper_panel": FanDamperController,
            "transport_panel": TransportController,
            "fresh_air_panel": FreshAirController,
            "vibration_panel": VibrationController,
            "hopper_heater_panel": HopperHeaterController,
            "cable_panel": CableController,
        }
        return {key: ctrl().build_panel() for key, ctrl in controllers.items()}

    def _populate_table_view(self, panel, table):
        df = pd.DataFrame(panel)
        df = self._add_summary_row(df)
        model = PandasModel(df)
        table.setModel(model)
        self._resize_columns(table, model)

    def _resize_columns(self, table, model):
        header = table.horizontalHeader()
        col_count = model.columnCount(None)
        for col in range(col_count - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(col_count - 1, QHeaderView.Stretch)
        table.resizeRowsToContents()

    def _add_summary_row(self, df):
        summary = {
            col: df[col].sum() if col == "total_price" else ("Total" if col.lower() == "type" else "")
            for col in df.columns
        }
        return pd.concat([df, pd.DataFrame([summary], index=["Total"])])

    def _refresh_tabs(self):
        self.tabWidget.clear()
        for table_name, tab_widget, label in self.all_tabs:
            model = self.tables[table_name].model()
            if model and self._should_show_tab(model._data):
                self.tabWidget.addTab(tab_widget, label)

    def _should_show_tab(self, df):
        if isinstance(df, pd.DataFrame):
            return "total_price" in df.columns and not df.empty and df.iloc[-1]["total_price"] > 0
        elif isinstance(df, list) and df and isinstance(df[-1], dict):
            return df[-1].get("Price", 0) > 0
        return False

    def _generate_summary_data(self, panels, electric_motor_price_and_info=None):
        summary = {"Title": [], "Price": [], "Note": [], "brands": []}
        total = 0

        for name, panel in panels.items():
            df = pd.DataFrame(panel)
            panel_total = df["total_price"].sum() if "total_price" in df.columns else 0
            if panel_total == 0:
                continue
            summary["Title"].append(name.replace("_", " ").title())
            summary["Price"].append(panel_total)
            summary["Note"].append("")
            summary["brands"].append({})
            total += panel_total

        if self.electrical_specs["fan"]["status"] and electric_motor_price_and_info:
            for motor in electric_motor_price_and_info:
                summary["Title"].append(motor["Title"])
                summary["Price"].append(motor["Price"])
                summary["Note"].append(motor["Note"])
                summary["brands"].append(motor["brands"])
                total += motor["Price"]

        summary["Title"].append("Total")
        summary["Price"].append(total)
        summary["Note"].append("")
        summary["brands"].append({})

        return summary

    def _set_summary_model(self, summary_data, use_brands=False):
        rows = pd.DataFrame(summary_data).to_dict(orient="records")
        model = SummaryTableModel(rows)
        table = self.tables["summary_table"]
        table.setModel(model)
        self._resize_columns(table, model)
        if use_brands:
            table.setItemDelegateForColumn(2, BrandComboDelegate(table))

    def _export_to_excel(self):
        """Handle user-initiated export to Excel with full report and factors."""
        file_name = f"{self.current_project.name}-{self.current_project.code}-{self.current_project.unique_no}-Rev{str(self.current_project.revision).zfill(2)}"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", file_name, "Excel Files (*.xlsx)")
        if not file_path:
            return

        try:
            report_path = file_path.replace(".xlsx", "(ReportByGriinPower).xlsx")

            # Collect tables and add installation table
            tables = {name: table for name, table in self.tables.items()}
            tables["installation_table"] = self.main_view.installation_tab.installation_table

            # Ensure summary_table and installation_table appear last
            keys = list(tables.keys())
            if "summary_table" in keys and "installation_table" in keys:
                keys.remove("summary_table")
                keys.remove("installation_table")
                keys += ["installation_table", "summary_table"]
                tables = {k: tables[k] for k in keys}

            # Call the report export method with tables
            self._export_report_excel(tables=tables, file_path=report_path)

            if sys.platform.startswith("win"):
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
                if isinstance(df, list):
                    df = pd.DataFrame(df)
                elif not isinstance(df, pd.DataFrame):
                    continue

                # Check for total_price column and its total row value
                if "total_price" in df.columns and df.iloc[-1]["total_price"] == 0:
                    continue  # Skip exporting this sheet

                df.index = range(1, len(df) + 1)
                df.to_excel(writer, sheet_name=name, index=True, startrow=1)
                self._style_excel_sheet(writer, name)

            # Append factor sheets
            instrument_df, summary_df = self._prepare_factor_data(tables)

            instrument_df.index = range(1, len(instrument_df) + 1)
            instrument_df.to_excel(writer, sheet_name="اقلام ابزار دقیق", startrow=1, index=False)
            self._style_excel_sheet(writer, "اقلام ابزار دقیق")

            summary_df.index = range(1, len(summary_df) + 1)
            summary_df.to_excel(writer, sheet_name="قیمت نهایی", startrow=1, index=False)
            self._style_excel_sheet(writer, "قیمت نهایی")

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

    def _prepare_factor_data(self, tables):
        """Generates instrument and summary DataFrames for factor sheets."""
        instruments_list = [
            'Delta Pressure Transmitter', 'Delta Pressure Switch', 'Pressure Transmitter',
            'Pressure Switch', 'Pressure Gauge', 'Temperature Transmitter', 'Proximity Switch',
            'Vibration Transmitter', 'Speed Detector', 'Level Switch', 'Level Transmitter', 'Pt100',
            'Ways Manifold', 'Calibration'
        ]

        bagfilter_price = 0
        instruments_price = 0
        cable_price = 0
        instrument_items = []

        for name, table in tables.items():
            if name in ("summary_table", "installation_table"):
                continue

            model = table.model()
            if model is None:
                continue

            df_raw = model._data
            if isinstance(df_raw, list):
                df = pd.DataFrame(df_raw)
            elif isinstance(df_raw, pd.DataFrame):
                df = df_raw.copy()
            else:
                raise TypeError(f"Unexpected type for model._data: {type(df_raw)}")

            df = df.drop(columns=["brands"], errors="ignore")
            df.columns = df.columns.str.lower()

            if name == "cable_table":
                cable_price = df.iloc[-1].get('total_price', 0)
                continue

            for _, row in df.iterrows():
                if str(row.get("type", "")).lower() == "total":
                    continue

                if any(inst in str(row.get("type", "")) for inst in instruments_list):
                    instruments_price += row.get('total_price', 0)
                    instrument_items.append({
                        "شرح": row.get("type", ""),
                        "برند": row.get("brand", ""),
                        "تعداد": row.get("quantity", 1),
                        "قیمت واحد": row.get("price", 0),
                        "قیمت کل": row.get("total_price", 0),
                    })

            bagfilter_price += df.iloc[-1].get('total_price', 0)

        bagfilter_price -= instruments_price

        # Electric motor info
        el_motor_price = 0
        el_motor_desc = ""

        summary_model = tables.get('summary_table').model()
        if summary_model:
            summary_data = summary_model._data
            if isinstance(summary_data, list):
                for row in summary_data:
                    if isinstance(row, dict) and "Electric Motor" in row.get("Title", ""):
                        el_motor_price += row.get("Price", 0)

            fan_motor = self.electrical_specs.get("fan", {}).get("motors", {}).get("fan", {})
            if fan_motor:
                el_motor_desc = f" الکتروموتور {int(fan_motor.get('power', 0) / 1000)}KW " \
                                f"{fan_motor.get('brand', '')} {fan_motor.get('efficiency_class', '')}"
            else:
                el_motor_desc = "الکتروموتور"

        # Build summary DataFrame
        summary_data = [
            [0, 0, 0, bagfilter_price, bagfilter_price, 1, "تابلوبگ فیلتر", 1],
            [0, 0, 0, instruments_price, instruments_price, 1, "ابزار دقیق", 2],
            [0, 0, 0, cable_price, cable_price, 1, "کابل", 3],
            [0, 0, 0, 0, 0, 1, "راه اندازی FAT", 4],
            [0, 0, 0, el_motor_price, el_motor_price, 1, el_motor_desc, 5]
        ]

        summary_df = pd.DataFrame(summary_data, columns=[
            "خرید", "مهندسی", "ساخت", "قیمت کل(ریال)", "قیمت", "تعداد", "شرح", "ردیف"
        ])
        summary_totals = summary_df[["خرید", "مهندسی", "ساخت", "قیمت کل(ریال)", "قیمت"]].sum().to_dict()
        summary_df.loc[len(summary_df)] = {**summary_totals, "تعداد": "", "شرح": "جمع کل", "ردیف": ""}

        instrument_df = pd.DataFrame(instrument_items)

        if not instrument_df.empty:
            instrument_df.insert(0, "ردیف", range(1, len(instrument_df) + 1))
            total_price = instrument_df["قیمت کل"].sum()
            instrument_df.loc[len(instrument_df)] = {
                "ردیف": "", "شرح": "جمع کل", "برند": "", "تعداد": "",
                "قیمت واحد": "", "قیمت کل": total_price
            }
            instrument_df = instrument_df[instrument_df.columns[::-1]]

        return instrument_df, summary_df


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


class SummaryTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data  # list of dicts with keys: Title, Price, Note, brands

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["Title", "Price", "Note"]
            if section < len(headers):
                return headers[section]
        return super().headerData(section, orientation, role)

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        item = self._data[row]
        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 0:
                return item["Title"]
            elif col == 1:
                if role == Qt.DisplayRole:
                    return "{:,}".format(item["Price"])  # نمایش هزارگان برای حالت نمایشی
                elif role == Qt.EditRole:
                    return item["Price"]  # مقدار اصلی برای ویرایش

        elif col == 2:
            return item["Note"]

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        row, col = index.row(), index.column()

        if col == 2 and row < self.rowCount() - 1:  # تغییر برند مجاز به جز Total
            item = self._data[row]
            item["Note"] = value
            item["Price"] = item["brands"].get(value, item["Price"])
            self.dataChanged.emit(self.index(row, 1), self.index(row, 1))
            self.dataChanged.emit(index, index)
            self._update_total()
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 2 and index.row() < self.rowCount() - 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def _update_total(self):
        total_row = self.rowCount() - 1
        total = sum(row["Price"] for row in self._data[:-1])
        self._data[total_row]["Price"] = total
        self.dataChanged.emit(self.index(total_row, 1), self.index(total_row, 1))


class BrandComboDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        row = index.row()
        brands_dict = index.model()._data[row].get("brands", {})
        if not brands_dict:
            return None  # برند ندارد، ComboBox لازم نیست
        combo = QComboBox(parent)
        combo.addItems(list(brands_dict.keys()))
        return combo

    def setEditorData(self, editor, index):
        current = index.model().data(index, Qt.EditRole)
        idx = editor.findText(current)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

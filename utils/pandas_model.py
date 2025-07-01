import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt

from views.message_box_view import show_message


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data.copy()

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None

        value = self._data.iat[index.row(), index.column()]
        column_name = self._data.columns[index.column()]

        # Convert boolean strings to "Yes" or "No"
        if str(value).lower() == "true":
            return "Yes"
        elif str(value).lower() == "false":
            return "No"

        # Existing formatting logic for price columns
        if column_name.lower() in {"price", "total_price"} and pd.notnull(value):
            try:
                value = float(value)
                return f"{value:,.0f}" if value.is_integer() else f"{value:,.2f}"
            except (ValueError, TypeError):
                return str(value)

        return str(value)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        try:
            row, col = index.row(), index.column()
            dtype = self._data.dtypes[col]
            self._data.iat[row, col] = dtype.type(value)
            self.dataChanged.emit(index, index)
            return True
        except Exception as e:
            show_message(f"Failed to set data at ({row}, {col}): {e}", "Error")
            return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._data.columns[section].replace("_", " ").title()
        if orientation == Qt.Vertical:
            return str(self._data.index[section])
        return None

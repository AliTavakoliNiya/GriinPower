from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt


def show_message(message: str, title: str = ""):
    msg = QMessageBox()
    msg.setWindowIcon(QIcon('assets/Logo.ico'))
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()



# Sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'San Francisco', 'Los Angeles']
})

# Custom model to display pandas DataFrame in QTableView
class PandasModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iat[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return section +1
        return None

# PyQt App
class ShowTable(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("Info")

        view = QTableView()
        model = PandasModel(df)
        view.setModel(model)
        view.resizeColumnsToContents()
        view.resizeRowsToContents()

        # Auto-resize the window to fit the content
        total_width = sum([view.columnWidth(i) for i in range(model.columnCount())])
        total_height = sum([view.rowHeight(i) for i in range(model.rowCount())])

        # Add a little extra padding for headers and borders
        total_width += view.verticalHeader().width() + 20
        total_height += view.horizontalHeader().height() + 60

        self.setCentralWidget(view)
        self.resize(total_width, total_height)

        self.show()





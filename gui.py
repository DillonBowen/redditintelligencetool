import sys
from typing import Dict, List, Optional

from PyQt5 import QtCore, QtWidgets

from app.core import generate_report, get_reddit_instance, save_to_csv


class ReportWorker(QtCore.QThread):
    row_ready = QtCore.pyqtSignal(dict)
    completed = QtCore.pyqtSignal(list)
    error = QtCore.pyqtSignal(str)

    def __init__(self, subreddit: str, report_type: str, parent=None):
        super().__init__(parent)
        self.subreddit = subreddit
        self.report_type = report_type

    def run(self):
        try:
            reddit = get_reddit_instance()
            collected_rows: List[Dict[str, object]] = []

            def on_row(row: Dict[str, object]):
                collected_rows.append(row)
                self.row_ready.emit(row)

            data = generate_report(
                reddit,
                self.subreddit,
                self.report_type,
                row_callback=on_row,
            )
            # In case the generator returns rows without invoking the callback
            if not collected_rows and data:
                for row in data:
                    self.row_ready.emit(row)
            self.completed.emit(data or collected_rows)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


class RedditReportWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.worker: Optional[ReportWorker] = None
        self.current_data: List[Dict[str, object]] = []
        self.setWindowTitle('Reddit Intelligence Tool')
        self.resize(800, 600)

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        self.subreddit_input = QtWidgets.QLineEdit()
        form_layout.addRow('Subreddit:', self.subreddit_input)

        self.report_type_combo = QtWidgets.QComboBox()
        self.report_type_combo.addItems(['overview', 'detailed'])
        form_layout.addRow('Report Type:', self.report_type_combo)

        output_layout = QtWidgets.QHBoxLayout()
        self.output_input = QtWidgets.QLineEdit()
        self.output_browse = QtWidgets.QPushButton('Browse...')
        self.output_browse.clicked.connect(self._browse_output)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.output_browse)
        form_layout.addRow('Output CSV (optional):', output_layout)

        layout.addLayout(form_layout)

        self.generate_button = QtWidgets.QPushButton('Generate Report')
        self.generate_button.clicked.connect(self.start_report)
        layout.addWidget(self.generate_button)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Title', 'Author', 'Score', 'Comments', 'URL'])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.save_button = QtWidgets.QPushButton('Save CSV')
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_csv)
        layout.addWidget(self.save_button)

    def _browse_output(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Select CSV file', filter='CSV Files (*.csv);;All Files (*)')
        if filename:
            self.output_input.setText(filename)

    def start_report(self):
        subreddit = self.subreddit_input.text().strip()
        report_type = self.report_type_combo.currentText()

        if not subreddit:
            self._show_message('Validation Error', 'Please enter a subreddit name.')
            return

        self.table.setRowCount(0)
        self.current_data = []
        self.save_button.setEnabled(False)
        self.generate_button.setEnabled(False)

        self.worker = ReportWorker(subreddit, report_type)
        self.worker.row_ready.connect(self._add_row)
        self.worker.completed.connect(self._on_completed)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _add_row(self, row_data: Dict[str, object]):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(row_data.get('title', ''))))
        self.table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(row_data.get('author', ''))))
        self.table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(row_data.get('score', ''))))
        self.table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(row_data.get('comments', ''))))
        self.table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(row_data.get('url', ''))))

    def _on_completed(self, data: List[Dict[str, object]]):
        self.current_data = data
        self.save_button.setEnabled(bool(data))

    def _on_error(self, message: str):
        self._show_message('Error', message)

    def _on_finished(self):
        self.generate_button.setEnabled(True)

    def save_csv(self):
        if not self.current_data:
            self._show_message('No Data', 'There is no data to save yet.')
            return

        filename = self.output_input.text().strip()
        if not filename:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save CSV', filter='CSV Files (*.csv);;All Files (*)')
            if not filename:
                return

        try:
            save_to_csv(self.current_data, filename)
            self._show_message('Success', f'Data saved to {filename}')
        except Exception as exc:  # noqa: BLE001
            self._show_message('Error', str(exc))

    def _show_message(self, title: str, message: str):
        QtWidgets.QMessageBox.information(self, title, message)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = RedditReportWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

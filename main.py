import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow
from services.storage_service import StorageService
from services.report_service import ReportService


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow { background: #f5f5f5; }
        * { font-family: 'Segoe UI', 'Arial', sans-serif; }
    """)

    storage = StorageService("data.json")
    report = ReportService("report.txt")

    window = MainWindow(storage, report)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
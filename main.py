import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from screens import MainWindow
from updater import check_for_updates, download_and_install

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #F9F3E6, stop:1 #FFE4B5);
        }
        QWidget {
            font-family: "Comic Sans MS", "Segoe UI Emoji", cursive;
        }
        QPushButton {
            background-color: #FFB74D;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: #5D3A1A;
        }
        QPushButton:hover {
            background-color: #FFA726;
        }
        QPushButton:pressed {
            background-color: #F57C00;
        }
        QListWidget {
            background-color: #FFF8E7;
            border-radius: 15px;
            padding: 5px;
            font-size: 14px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background-color: #FFB74D;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #FFE0B2;
        }
        QLabel {
            color: #5D3A1A;
        }
    """)

    window = MainWindow()
    window.show()

    # Проверка обновлений после показа окна
    has_update, latest_version, url = check_for_updates()
    if has_update and url:
        reply = QMessageBox.question(
            window,
            "Доступно обновление",
            f"Доступна новая версия {latest_version}. Установить сейчас?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            download_and_install(url, window)
            sys.exit(0)  # после запуска установщика выходим

    sys.exit(app.exec_())
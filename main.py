import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QSettings
from screens import MainWindow
from updater import check_for_updates, download_and_install

if __name__ == "__main__":
    app = QApplication(sys.argv)

    settings = QSettings("MuseumApp", "MuseumApp")
    last_theme = settings.value("theme", "Тёплая")

    window = MainWindow()
    window.apply_theme(last_theme)
    window.start_screen.theme_changed.connect(lambda t: settings.setValue("theme", t))
    window.showMaximized()   # вместо window.show()

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
            sys.exit(0)

    sys.exit(app.exec_())
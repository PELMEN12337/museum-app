from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from version import VERSION


class VersionLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText(f"Версия {VERSION}")
        self.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")
        self.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.setFixedHeight(20)

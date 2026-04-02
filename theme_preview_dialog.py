from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QWidget, QLabel
from PyQt5.QtCore import Qt
from themes import THEMES

class ThemePreviewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор темы")
        self.setMinimumSize(600, 400)
        layout = QHBoxLayout(self)

        self.list = QListWidget()
        self.list.addItems(THEMES.keys())
        self.list.currentItemChanged.connect(self.on_theme_selected)
        layout.addWidget(self.list)

        self.preview = QWidget()
        self.preview.setFixedSize(300, 200)
        self.preview_layout = QVBoxLayout(self.preview)
        self.preview_label = QLabel("Пример текста")
        self.preview_btn = QPushButton("Кнопка")
        self.preview_layout.addWidget(self.preview_label)
        self.preview_layout.addWidget(self.preview_btn)
        layout.addWidget(self.preview)

        self.ok_btn = QPushButton("Выбрать")
        self.ok_btn.clicked.connect(self.accept)
        layout.addWidget(self.ok_btn)

        self.selected_theme = None

    def on_theme_selected(self, current, previous):
        if current:
            theme_name = current.text()
            style = THEMES.get(theme_name, "")
            self.preview.setStyleSheet(style)
            self.selected_theme = theme_name

    def accept(self):
        if self.selected_theme:
            super().accept()
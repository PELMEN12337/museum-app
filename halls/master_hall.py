from PyQt5.QtCore import Qt

from .base_hall import BaseHallLevel
from PyQt5.QtWidgets import QLabel

class MasterHallLevel(BaseHallLevel):
    """Зал мастера: Подбери цвета по картинке"""
    def setup_content(self):
        if self.preset_data:
            label = QLabel(f"Уровень {self.level}: подберите цвета (пресет)")
        else:
            label = QLabel(f"Уровень {self.level}: подберите цвета")
        label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(label)
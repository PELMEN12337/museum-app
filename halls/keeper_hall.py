from PyQt5.QtCore import Qt

from .base_hall import BaseHallLevel
from PyQt5.QtWidgets import QLabel

class KeeperHallLevel(BaseHallLevel):
    """Зал хранителя: Сортировка по коллекциям"""
    def setup_content(self):
        if self.preset_data:
            label = QLabel(f"Уровень {self.level}: отсортируйте экспонаты (пресет)")
        else:
            label = QLabel(f"Уровень {self.level}: отсортируйте экспонаты")
        label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(label)
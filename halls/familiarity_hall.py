from PyQt5.QtCore import Qt

from .base_hall import BaseHallLevel
from PyQt5.QtWidgets import QLabel

class FamiliarityHallLevel(BaseHallLevel):
    """Зал знакомства: Найди такую же"""
    def setup_content(self):
        if self.preset_data:
            # Здесь будет логика с изображениями для поиска одинаковых
            label = QLabel(f"Уровень {self.level}: найдите такую же картинку (пресет)")
        else:
            label = QLabel(f"Уровень {self.level}: найдите такую же картинку")
        label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(label)
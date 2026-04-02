from PyQt5.QtCore import Qt

from .base_hall import BaseHallLevel
from PyQt5.QtWidgets import QLabel

class RestorerHallLevel(BaseHallLevel):
    """Зал реставратора: Заплатки"""
    def setup_content(self):
        if self.preset_data:
            label = QLabel(f"Уровень {self.level}: исправьте повреждения (пресет)")
        else:
            label = QLabel(f"Уровень {self.level}: исправьте повреждения")
        label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(label)
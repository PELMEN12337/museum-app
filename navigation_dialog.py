from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from constants import HALLS

class NavigationDialog(QDialog):
    def __init__(self, parent, current_hall, current_level):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Навигация")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #CCC;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:selected {
                background-color: #FFB74D;
                color: white;
            }
            QPushButton {
                background-color: #FFB74D;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA726;
            }
            QLabel {
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)

        label = QLabel("Выберите зал и уровень:")
        layout.addWidget(label)

        self.hall_list = QListWidget()
        layout.addWidget(self.hall_list)

        self.level_list = QListWidget()
        layout.addWidget(self.level_list)

        # Получаем текущий выбранный пресет из главного окна
        self.current_preset = None
        if parent and hasattr(parent, 'current_preset'):
            self.current_preset = parent.current_preset

        # Список всех залов
        self.hall_names = list(HALLS.keys())
        self.hall_levels = {}

        # Определяем количество уровней для каждого зала (из пресета или стандартное)
        for hall_name in self.hall_names:
            if self.current_preset and hall_name in self.current_preset.get("halls", {}):
                levels_count = len(self.current_preset["halls"][hall_name]["levels"])
            else:
                levels_count = HALLS[hall_name]
            self.hall_levels[hall_name] = levels_count
            item = QListWidgetItem(f"{hall_name} (уровней: {levels_count})")
            self.hall_list.addItem(item)

        # Подключаем сигнал выбора зала
        self.hall_list.itemClicked.connect(self.on_hall_selected)

        # Выбираем текущий зал и уровень
        current_index = self.hall_names.index(current_hall)
        self.hall_list.setCurrentRow(current_index)
        self.on_hall_selected(self.hall_list.currentItem())

        # Выбираем текущий уровень в списке уровней
        for i in range(self.level_list.count()):
            if int(self.level_list.item(i).text()) == current_level:
                self.level_list.setCurrentItem(self.level_list.item(i))
                break

        # Кнопки
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Перейти")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.selected_hall = None
        self.selected_level = None

    def on_hall_selected(self, item):
        """При выборе зала заполняем список уровней."""
        hall_name = self.hall_names[self.hall_list.currentRow()]
        self.selected_hall = hall_name
        total_levels = self.hall_levels[hall_name]
        self.level_list.clear()
        for level in range(1, total_levels + 1):
            self.level_list.addItem(str(level))

    def get_selection(self):
        """Возвращает выбранный зал и уровень."""
        hall = self.selected_hall
        level_item = self.level_list.currentItem()
        level = int(level_item.text()) if level_item else None
        return hall, level
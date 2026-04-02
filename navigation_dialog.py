from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
from constants import HALLS

class NavigationDialog(QDialog):
    def __init__(self, parent, current_hall, current_level):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Навигация")
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; }
            QListWidget { background-color: white; border: 1px solid #CCC; border-radius: 6px; }
            QListWidget::item:selected { background-color: #FFB74D; color: white; }
            QPushButton { background-color: #FFB74D; border: none; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #FFA726; }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Выберите зал и уровень:"))

        self.hall_list = QListWidget()
        layout.addWidget(self.hall_list)

        self.level_list = QListWidget()
        layout.addWidget(self.level_list)

        self.current_preset = getattr(parent, 'current_preset', None)

        self.hall_levels = {}
        if self.current_preset and "halls" in self.current_preset:
            for hall_name, hall_data in self.current_preset["halls"].items():
                levels_count = len(hall_data["levels"])
                self.hall_levels[hall_name] = levels_count
        else:
            for hall_name in HALLS:
                self.hall_levels[hall_name] = HALLS[hall_name]

        self.hall_names = list(self.hall_levels.keys())
        for hall_name in self.hall_names:
            levels_count = self.hall_levels[hall_name]
            item = QListWidgetItem(f"{hall_name} (уровней: {levels_count})")
            self.hall_list.addItem(item)

        self.hall_list.itemClicked.connect(self.on_hall_selected)

        if current_hall in self.hall_names:
            current_index = self.hall_names.index(current_hall)
            self.hall_list.setCurrentRow(current_index)
        else:
            current_index = 0
            self.hall_list.setCurrentRow(current_index)
        self.on_hall_selected(self.hall_list.currentItem())

        self.level_list.itemClicked.connect(self.on_level_selected)

        total_levels = self.hall_levels[self.hall_names[current_index]]
        self.selected_level = None
        if 1 <= current_level <= total_levels:
            for i in range(self.level_list.count()):
                if int(self.level_list.item(i).text()) == current_level:
                    self.level_list.setCurrentItem(self.level_list.item(i))
                    self.selected_level = current_level
                    break
        if self.selected_level is None and self.level_list.count() > 0:
            self.level_list.setCurrentRow(0)
            self.selected_level = 1

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("Перейти")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.selected_hall = current_hall if current_hall in self.hall_names else self.hall_names[0]

    def on_hall_selected(self, item):
        hall_name = self.hall_names[self.hall_list.currentRow()]
        self.selected_hall = hall_name
        total_levels = self.hall_levels[hall_name]
        self.level_list.clear()
        for level in range(1, total_levels + 1):
            self.level_list.addItem(str(level))
        if self.level_list.count() > 0:
            self.level_list.setCurrentRow(0)
            self.selected_level = 1

    def on_level_selected(self, item):
        self.selected_level = int(item.text())

    def get_selection(self):
        return self.selected_hall, self.selected_level
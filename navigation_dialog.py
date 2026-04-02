from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QLabel)
from constants import HALLS   # <-- импорт из constants

class NavigationDialog(QDialog):
    def __init__(self, parent, current_hall, current_level):
        super().__init__(parent)
        self.setWindowTitle("Навигация")
        self.setMinimumSize(400, 300)

        self.current_hall = current_hall
        self.current_level = current_level

        layout = QVBoxLayout(self)

        label = QLabel("Выберите зал и уровень:")
        layout.addWidget(label)

        self.hall_list = QListWidget()
        for hall_name in HALLS.keys():
            item = QListWidgetItem(hall_name)
            self.hall_list.addItem(item)
        layout.addWidget(self.hall_list)

        self.level_list = QListWidget()
        layout.addWidget(self.level_list)

        self.hall_list.itemClicked.connect(self.on_hall_selected)

        current_index = list(HALLS.keys()).index(current_hall)
        self.hall_list.setCurrentRow(current_index)
        self.on_hall_selected(self.hall_list.currentItem())

        for i in range(self.level_list.count()):
            item = self.level_list.item(i)
            if int(item.text()) == current_level:
                self.level_list.setCurrentItem(item)
                break

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Перейти")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.selected_hall = None
        self.selected_level = None

    def on_hall_selected(self, item):
        self.selected_hall = item.text()
        total_levels = HALLS[self.selected_hall]
        self.level_list.clear()
        for level in range(1, total_levels + 1):
            self.level_list.addItem(str(level))

    def get_selection(self):
        hall = self.selected_hall
        level_item = self.level_list.currentItem()
        level = int(level_item.text()) if level_item else None
        return hall, level
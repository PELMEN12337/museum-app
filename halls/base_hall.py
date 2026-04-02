from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BaseHallLevel(QWidget):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        super().__init__(parent)
        self.parent = parent
        self.hall_name = hall_name
        self.level = level
        self.total_levels = total_levels
        self.preset_data = preset_data

        # Основной layout – вертикальный
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Заголовок
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(self.title_label)

        # Информация об уровне
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.info_label)

        # Контейнер для содержимого зала (картинки и т.д.)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.layout.addWidget(self.content_widget, stretch=1)  # растягивается

        # Панель кнопок внизу
        self.button_panel = QWidget()
        button_layout = QVBoxLayout(self.button_panel)
        button_layout.setContentsMargins(0, 10, 0, 0)

        # Кнопка навигации
        self.nav_btn = QPushButton("Навигация по залам и уровням")
        self.nav_btn.clicked.connect(self.open_navigation)
        button_layout.addWidget(self.nav_btn, alignment=Qt.AlignCenter)

        # Кнопки переключения уровней
        level_switch_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Предыдущий уровень")
        self.prev_btn.clicked.connect(self.prev_level)
        self.next_btn = QPushButton("Следующий уровень")
        self.next_btn.clicked.connect(self.next_level)
        level_switch_layout.addWidget(self.prev_btn)
        level_switch_layout.addWidget(self.next_btn)
        button_layout.addLayout(level_switch_layout)

        # Кнопка выбора другого зала
        self.hall_btn = QPushButton("Выбор другого зала")
        self.hall_btn.clicked.connect(self.go_to_hall_selection)
        button_layout.addWidget(self.hall_btn, alignment=Qt.AlignCenter)

        self.layout.addWidget(self.button_panel)

        # Инициализация отображения
        self.update_display()
        self.setup_content()

    def update_display(self):
        self.title_label.setText(self.hall_name)
        self.info_label.setText(f"Уровень {self.level} из {self.total_levels}")
        self.prev_btn.setEnabled(self.level > 1)
        self.next_btn.setEnabled(self.level < self.total_levels)

    def prev_level(self):
        if self.level > 1:
            self.parent.show_level(self.hall_name, self.level - 1)

    def next_level(self):
        if self.level < self.total_levels:
            self.parent.show_level(self.hall_name, self.level + 1)

    def go_to_hall_selection(self):
        if self.parent:
            self.parent.show_hall_selection_from_level()

    def open_navigation(self):
        from navigation_dialog import NavigationDialog
        dialog = NavigationDialog(self.parent, self.hall_name, self.level)
        if dialog.exec_():
            hall, level = dialog.get_selection()
            if hall and level:
                self.parent.navigate_to(hall, level)

    def setup_content(self):
        placeholder = QLabel("Содержимое уровня будет здесь")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("background-color: #FFF8E7; border-radius: 15px; padding: 20px;")
        self.content_layout.addWidget(placeholder)
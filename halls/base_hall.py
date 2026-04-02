from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import QShortcut

class BaseHallLevel(QWidget):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        super().__init__(parent)
        self.parent = parent
        self.hall_name = hall_name
        self.level = level
        self.total_levels = total_levels
        self.preset_data = preset_data

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.layout.addWidget(self.title_label)

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.info_label)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.layout.addWidget(self.content_widget)

        # Горизонтальный блок для двух кнопок: навигация и полноэкранный режим
        button_row = QHBoxLayout()
        self.nav_btn = QPushButton("Навигация по залам и уровням")
        self.nav_btn.clicked.connect(self.open_navigation)
        button_row.addWidget(self.nav_btn)

        self.fullscreen_btn = QPushButton("На весь экран")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        button_row.addWidget(self.fullscreen_btn)

        self.layout.addLayout(button_row)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Предыдущий уровень")
        self.prev_btn.clicked.connect(self.prev_level)
        self.next_btn = QPushButton("Следующий уровень")
        self.next_btn.clicked.connect(self.next_level)
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        self.layout.addLayout(btn_layout)

        self.hall_btn = QPushButton("Выбор другого зала")
        self.hall_btn.clicked.connect(self.go_to_hall_selection)
        self.layout.addWidget(self.hall_btn, alignment=Qt.AlignCenter)

        from version_label import VersionLabel
        self.version_label = VersionLabel(self)
        self.layout.addWidget(self.version_label, alignment=Qt.AlignRight | Qt.AlignBottom)

        self.update_display()
        self.setup_content()

        # Шорткат F11 для полноэкранного режима
        self.fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.toggle_fullscreen)

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

    def toggle_fullscreen(self):
        if self.parent:
            if self.parent.isFullScreen():
                self.parent.showNormal()
            else:
                self.parent.showFullScreen()

    def setup_content(self):
        placeholder = QLabel("Содержимое уровня будет здесь")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("background-color: #FFF8E7; border-radius: 15px; padding: 20px;")
        self.content_layout.addWidget(placeholder)
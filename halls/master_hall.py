import random
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
from .base_hall import BaseHallLevel
from constants import get_next_hall

def crop_to_square(pixmap):
    """Обрезает QPixmap до квадрата по центру."""
    if pixmap.isNull():
        return pixmap
    w = pixmap.width()
    h = pixmap.height()
    if w == h:
        return pixmap
    side = min(w, h)
    x = (w - side) // 2
    y = (h - side) // 2
    return pixmap.copy(QRect(x, y, side, side))

class MasterHallLevel(BaseHallLevel):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        self.main_label = None
        self.color_buttons = []
        self.correct_indices = []
        self.selected_indices = set()
        self.submit_button = None
        self.shuffled_paths = []
        self.shuffled_indices = []
        self.main_path = None
        super().__init__(parent, hall_name, level, total_levels, preset_data)

    def setup_content(self):
        if not self.preset_data:
            label = QLabel(f"Уровень {self.level}: подберите цвета по картинке")
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)
            return

        self.content_layout.addSpacing(60)

        level_index = self.level - 1
        level_info = self.preset_data["levels"][level_index]
        main_path = level_info["main_image"]
        color_paths = level_info["color_images"]
        self.correct_indices = level_info.get("correct_indices", [0,1,2,3])

        indexed = list(enumerate(color_paths))
        random.shuffle(indexed)
        self.shuffled_paths = [path for _, path in indexed]
        self.shuffled_indices = [orig_idx for orig_idx, _ in indexed]

        main_layout = QHBoxLayout()
        self.content_layout.addLayout(main_layout)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(0, 0, 0, 0)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(0, 0, 0, 0)

        center_layout = QVBoxLayout()
        self.main_label = QLabel()
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_label.setStyleSheet("border: 2px solid #FFB74D; border-radius: 10px; background-color: #FFF8E7;")
        center_layout.addWidget(self.main_label, alignment=Qt.AlignCenter)

        main_layout.addStretch()
        main_layout.addLayout(left_layout)
        main_layout.addSpacing(150)
        main_layout.addLayout(center_layout)
        main_layout.addSpacing(150)
        main_layout.addLayout(right_layout)
        main_layout.addStretch()

        for i, path in enumerate(self.shuffled_paths):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid gray;
                    border-radius: 5px;
                    background-color: white;
                    padding: 2px;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.toggle_color(idx))
            self.color_buttons.append(btn)

        for i in range(4):
            left_layout.addWidget(self.color_buttons[i])
        for i in range(4, 8):
            right_layout.addWidget(self.color_buttons[i])

        self.content_layout.addSpacing(30)
        self.submit_button = QPushButton("Проверить")
        self.submit_button.clicked.connect(self.check_answer)
        self.content_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

        self.load_main_image(main_path)
        self.load_color_images()

        if self.level == self.total_levels:
            self.next_hall_btn = QPushButton("➡️ Перейти к следующему залу")
            self.next_hall_btn.clicked.connect(self.go_to_next_hall)
            self.next_hall_btn.setVisible(False)
            self.layout.addWidget(self.next_hall_btn, alignment=Qt.AlignCenter)

    def load_color_images(self):
        for btn, path in zip(self.color_buttons, self.shuffled_paths):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                square = crop_to_square(pixmap)
                scaled = square.scaled(btn.width() - 10, btn.height() - 10, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                btn.setIcon(QIcon(scaled))
                btn.setIconSize(btn.size() - QSize(10, 10))
            else:
                btn.setText("Ошибка")
        self.update_selection_styles()

    def update_selection_styles(self):
        for idx, btn in enumerate(self.color_buttons):
            if idx in self.selected_indices:
                btn.setStyleSheet("""
                    QPushButton {
                        border: 10px solid green;
                        border-radius: 1px;
                        background-color: #E8F5E9;
                        padding: 2px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        border: 10px solid gray;
                        border-radius: 1px;
                        background-color: white;
                        padding: 2px;
                    }
                """)

    def load_main_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.main_label.setPixmap(pixmap)
            self.main_label.setScaledContents(False)
        else:
            self.main_label.setText("Ошибка загрузки")
        self.main_path = path

    def toggle_color(self, idx):
        if idx in self.selected_indices:
            self.selected_indices.remove(idx)
        else:
            self.selected_indices.add(idx)
        self.update_selection_styles()

    def check_answer(self):
        selected_original = [self.shuffled_indices[i] for i in self.selected_indices]
        correct_original = set(self.correct_indices)
        if set(selected_original) == correct_original:
            self.show_custom_message("Правильно!", "green")
            if self.level < self.total_levels:
                self.parent.show_level(self.hall_name, self.level + 1)
            else:
                if self.next_hall_btn:
                    self.next_hall_btn.setVisible(True)
        else:
            self.show_custom_message("Попробуйте ещё раз!", "red")

    def update_sizes(self):
        if not self.color_buttons:
            return
        parent_widget = self.content_widget
        if not parent_widget:
            return
        available_width = parent_widget.width() - 60
        btn_size = max(60, min(available_width // 6, 120))
        icon_size = btn_size - 4
        for btn in self.color_buttons:
            btn.setFixedSize(btn_size, btn_size)
            btn.setIconSize(QSize(icon_size, icon_size))
        main_size = min(available_width // 2, 600)
        self.main_label.setFixedSize(main_size, main_size)
        if self.main_path:
            pixmap = QPixmap(self.main_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(main_size, main_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.main_label.setPixmap(scaled)
        self.load_color_images()

    def resizeEvent(self, event):
        self.update_sizes()
        super().resizeEvent(event)

    def showEvent(self, event):
        self.update_sizes()
        super().showEvent(event)

    def show_custom_message(self, text, color):
        msg = QDialog(self)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        msg.setStyleSheet(f"background-color: {color};")
        layout = QVBoxLayout(msg)
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"font-size: 48px; font-weight: bold; color: white; padding: 40px;")
        layout.addWidget(label)
        QTimer.singleShot(1500, msg.accept)
        msg.exec_()

    def go_to_next_hall(self):
        next_hall = get_next_hall(self.hall_name)
        if next_hall:
            self.parent.show_level(next_hall, 1)
        else:
            self.parent.show_hall_selection_from_level()
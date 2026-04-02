import os
import random
from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QDialog, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from .base_hall import BaseHallLevel
from constants import get_next_hall

class AttentionHallLevel(BaseHallLevel):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        self.buttons = []
        self.original_pixmaps = []
        self.grid = None
        self.next_hall_btn = None
        self.level_data = []
        self.correct_answer = None
        self.display_to_original = []
        super().__init__(parent, hall_name, level, total_levels, preset_data)

    def setup_content(self):
        if self.preset_data:
            level_index = self.level - 1
            original_paths = self.preset_data["levels"][level_index]
            self.correct_answer = self.preset_data["correct_answers"][level_index]

            self.level_data = original_paths[:]
            indexed_paths = list(enumerate(original_paths))
            random.shuffle(indexed_paths)

            display_paths = []
            self.display_to_original = []
            for orig_idx, path in indexed_paths:
                display_paths.append(path)
                self.display_to_original.append(orig_idx)

            self.grid = QGridLayout()
            self.content_layout.addLayout(self.grid)

            for idx, img_path in enumerate(display_paths):
                label = QLabel()
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.original_pixmaps.append(pixmap)
                    scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    label.setPixmap(scaled)
                    label.setFixedSize(200, 200)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
                else:
                    self.original_pixmaps.append(None)
                    label.setText("Ошибка")
                    label.setFixedSize(200, 200)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
                label.mousePressEvent = lambda event, pos=idx: self.check_answer_by_position(pos)
                self.grid.addWidget(label, idx // 3, idx % 3)
                self.buttons.append(label)

            self.update_image_sizes()

            if self.level == self.total_levels:
                self.next_hall_btn = QPushButton("➡️ Перейти к следующему залу")
                self.next_hall_btn.clicked.connect(self.go_to_next_hall)
                self.next_hall_btn.setVisible(False)
                self.layout.addWidget(self.next_hall_btn, alignment=Qt.AlignCenter)
        else:
            label = QLabel(f"Уровень {self.level}: найдите лишний предмет")
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)

    def check_answer_by_position(self, display_position):
        original_idx = self.display_to_original[display_position]
        if original_idx == self.correct_answer:
            self.show_custom_message("Правильно!", "green")
            if self.level < self.total_levels:
                self.parent.show_level(self.hall_name, self.level + 1)
            else:
                if self.next_hall_btn:
                    self.next_hall_btn.setVisible(True)
        else:
            self.show_custom_message("Попробуйте ещё раз!", "red")

    def update_image_sizes(self):
        if not self.grid:
            return
        parent_widget = self.content_widget
        if not parent_widget:
            return
        available_width = parent_widget.width() - 20
        if available_width <= 0:
            return
        cols = 3
        spacing = self.grid.spacing()
        cell_size = (available_width - spacing * (cols - 1)) // cols
        cell_size = max(100, min(cell_size, 500))

        for idx, (label, pixmap) in enumerate(zip(self.buttons, self.original_pixmaps)):
            if pixmap is not None:
                scaled = pixmap.scaled(cell_size, cell_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled)
                label.setFixedSize(cell_size, cell_size)
            else:
                label.setFixedSize(cell_size, cell_size)

    def resizeEvent(self, event):
        self.update_image_sizes()
        super().resizeEvent(event)

    def show_custom_message(self, text, color):
        msg = QDialog(self)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        msg.setStyleSheet(f"background-color: {color};")
        layout = QVBoxLayout(msg)
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"font-size: 48px; font-weight: bold; color: white; padding: 40px;")
        layout.addWidget(label)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, msg.accept)
        msg.exec_()

    def go_to_next_hall(self):
        next_hall = get_next_hall(self.hall_name)
        if next_hall:
            self.parent.show_level(next_hall, 1)
        else:
            self.parent.show_hall_selection_from_level()
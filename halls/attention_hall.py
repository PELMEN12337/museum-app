import os
import random
from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QDialog, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from .base_hall import BaseHallLevel
from constants import get_next_hall

class AttentionHallLevel(BaseHallLevel):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        # Инициализация атрибутов
        self.labels = []
        self.original_pixmaps = []
        self.grid = None
        self.next_hall_btn = None
        self.level_data = []
        self.correct_answer = None
        self.display_to_original = []
        self.cols = 3
        super().__init__(parent, hall_name, level, total_levels, preset_data)

    def setup_content(self):
        if self.preset_data:
            level_index = self.level - 1
            original_paths = self.preset_data["levels"][level_index]
            self.correct_answer = self.preset_data["correct_answers"][level_index]

            # Перемешиваем порядок изображений
            indexed_paths = list(enumerate(original_paths))
            random.shuffle(indexed_paths)
            display_paths = []
            self.display_to_original = []
            for orig_idx, path in indexed_paths:
                display_paths.append(path)
                self.display_to_original.append(orig_idx)

            # Создаём сетку
            self.grid = QGridLayout()
            self.grid.setHorizontalSpacing(20)   # отступы по горизонтали
            self.grid.setVerticalSpacing(30)     # увеличенные отступы по вертикали
            self.content_layout.addLayout(self.grid)

            # Загружаем pixmap'ы и создаём метки
            for idx, img_path in enumerate(display_paths):
                label = QLabel()
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.original_pixmaps.append(pixmap)
                    label.setFixedSize(100, 100)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
                else:
                    self.original_pixmaps.append(None)
                    label.setText("Ошибка")
                    label.setFixedSize(100, 100)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
                label.mousePressEvent = lambda event, pos=idx: self.check_answer_by_position(pos)
                self.labels.append(label)

            # Перестраиваем сетку и масштабируем
            self.update_grid_layout()

            # Кнопка перехода к следующему залу (только для последнего уровня)
            if self.level == self.total_levels:
                self.next_hall_btn = QPushButton("➡️ Перейти к следующему залу")
                self.next_hall_btn.clicked.connect(self.go_to_next_hall)
                self.next_hall_btn.setVisible(False)
                self.layout.addWidget(self.next_hall_btn, alignment=Qt.AlignCenter)
        else:
            label = QLabel(f"Уровень {self.level}: найдите лишний предмет")
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)

    def update_grid_layout(self):
        """Определяет количество колонок и перестраивает сетку."""
        if not self.labels:
            return
        count = len(self.labels)
        # Определяем количество колонок
        if count <= 2:
            self.cols = 2
        elif count <= 4:
            self.cols = 3
        elif count <= 6:
            self.cols = 3
        else:
            self.cols = 4

        # Очищаем сетку
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Добавляем метки в сетку
        for idx, label in enumerate(self.labels):
            row = idx // self.cols
            col = idx % self.cols
            self.grid.addWidget(label, row, col)

        self.update_image_sizes()

    def update_image_sizes(self):
        """Вычисляет размер ячейки и масштабирует изображения."""
        if not self.labels or not self.content_widget:
            return
        available_width = self.content_widget.width() - 20
        if available_width <= 0:
            return
        h_spacing = self.grid.horizontalSpacing()
        cell_width = (available_width - h_spacing * (self.cols - 1)) // self.cols

        # Максимальный размер ячейки в зависимости от количества изображений
        img_count = len(self.labels)
        if img_count <= 3:
            max_cell = 500
        elif img_count <= 6:
            max_cell = 350
        else:
            max_cell = 250

        cell_size = max(100, min(cell_width, max_cell))

        for label, pixmap in zip(self.labels, self.original_pixmaps):
            if pixmap is not None:
                scaled = pixmap.scaled(cell_size, cell_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled)
                label.setFixedSize(cell_size, cell_size)
            else:
                label.setFixedSize(cell_size, cell_size)

    def resizeEvent(self, event):
        self.update_image_sizes()
        super().resizeEvent(event)

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
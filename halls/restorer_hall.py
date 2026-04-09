import random
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QSizePolicy, QWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
from .base_hall import BaseHallLevel
from constants import get_next_hall

class RestorerHallLevel(BaseHallLevel):
    # Настраиваемые параметры (измените здесь)
    MIN_HOLE_HEIGHT = 200
    MAX_HOLE_HEIGHT = 900
    MIN_COMPLETE_HEIGHT = 200
    MAX_COMPLETE_HEIGHT = 800
    MIN_PATCH_SIZE = 80
    MAX_PATCH_SIZE = 200

    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        self.hole_label = None
        self.options_buttons = []
        self.complete_label = None
        self.complete_container = None   # контейнер для целой картинки с отступом
        self.next_button = None
        self.correct_path = None
        self.shuffled_paths = []
        self.correct_index = None
        self.answer_given = False
        self.complete_image_path = None
        self.hole_image_path = None
        super().__init__(parent, hall_name, level, total_levels, preset_data)

    def setup_content(self):
        if not self.preset_data:
            label = QLabel(f"Уровень {self.level}: выберите подходящую заплатку")
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)
            return

        level_index = self.level - 1
        level_info = self.preset_data["levels"][level_index]
        self.complete_image_path = level_info["complete_image"]
        self.hole_image_path = level_info["hole_image"]
        patches = level_info["patches"]
        correct_patch_idx = level_info.get("correct_patch_idx", 0)

        indexed = list(enumerate(patches))
        random.shuffle(indexed)
        self.shuffled_paths = [path for _, path in indexed]
        for i, (orig_idx, _) in enumerate(indexed):
            if orig_idx == correct_patch_idx:
                self.correct_index = i
                break

        main_layout = QVBoxLayout()
        self.content_layout.addLayout(main_layout)

        self.hole_label = QLabel()
        self.hole_label.setAlignment(Qt.AlignCenter)
        self.hole_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hole_label.setStyleSheet("border: 2px solid #FFB74D; border-radius: 10px; background-color: #FFF8E7;")
        main_layout.addWidget(self.hole_label, alignment=Qt.AlignCenter)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        for idx, path in enumerate(self.shuffled_paths):
            btn = QPushButton()
            btn.setFixedSize(150, 150)
            btn.setIconSize(QSize(150, 150))
            btn.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
            btn.clicked.connect(lambda checked, i=idx: self.check_patch(i))
            options_layout.addWidget(btn)
            self.options_buttons.append(btn)
        main_layout.addLayout(options_layout)

        # Контейнер для целой картинки с отступом сверху
        self.complete_container = QWidget()
        complete_layout = QVBoxLayout(self.complete_container)
        complete_layout.setContentsMargins(0, 0, 0, 0)
        complete_layout.addSpacing(20)  # отступ сверху
        self.complete_label = QLabel()
        self.complete_label.setAlignment(Qt.AlignCenter)
        self.complete_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.complete_label.setStyleSheet("border: 2px solid #4CAF50; border-radius: 10px; background-color: #E8F5E9;")
        complete_layout.addWidget(self.complete_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.complete_container, alignment=Qt.AlignCenter)
        self.complete_container.hide()

        self.next_button = QPushButton("➡️ Далее")
        self.next_button.clicked.connect(self.go_to_next_level_or_hall)
        self.next_button.hide()
        main_layout.addWidget(self.next_button, alignment=Qt.AlignCenter)

        if self.level == self.total_levels:
            self.next_hall_btn = QPushButton("➡️ Перейти к следующему залу")
            self.next_hall_btn.clicked.connect(self.go_to_next_hall)
            self.next_hall_btn.hide()
            self.layout.addWidget(self.next_hall_btn, alignment=Qt.AlignCenter)

        self.update_sizes()

    def load_hole_image(self, target_height):
        target_height = max(self.MIN_HOLE_HEIGHT, min(target_height, self.MAX_HOLE_HEIGHT))
        pixmap = QPixmap(self.hole_image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaledToHeight(target_height, Qt.SmoothTransformation)
            self.hole_label.setPixmap(scaled)
            self.hole_label.setFixedSize(scaled.width(), scaled.height())
        else:
            self.hole_label.setText("Ошибка загрузки")

    def load_options_images(self):
        for btn, path in zip(self.options_buttons, self.shuffled_paths):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(btn.width(), btn.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                btn.setIcon(QIcon(scaled))
                btn.setIconSize(btn.size())
            else:
                btn.setText("Ошибка")

    def load_complete_image(self, target_height):
        target_height = max(self.MIN_COMPLETE_HEIGHT, min(target_height, self.MAX_COMPLETE_HEIGHT))
        pixmap = QPixmap(self.complete_image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaledToHeight(target_height, Qt.SmoothTransformation)
            self.complete_label.setPixmap(scaled)
            self.complete_label.setFixedSize(scaled.width(), scaled.height())
        else:
            self.complete_label.setText("Ошибка загрузки")

    def check_patch(self, idx):
        if self.answer_given:
            return
        if idx == self.correct_index:
            self.show_custom_message("Правильно!", "green")
            self.answer_given = True
            self.hole_label.hide()
            for btn in self.options_buttons:
                btn.hide()
            # Показываем контейнер с целой картинкой
            self.complete_container.show()
            # Принудительно обновляем размеры, чтобы целая картинка стала нужного размера
            self.update_sizes()
            if self.level == self.total_levels:
                if hasattr(self, 'next_hall_btn'):
                    self.next_hall_btn.show()
            else:
                self.next_button.show()
        else:
            self.show_custom_message("Попробуйте ещё раз!", "red")

    def update_sizes(self):
        if not self.options_buttons:
            return
        parent_widget = self.content_widget
        if not parent_widget:
            return
        available_width = parent_widget.height() - 60
        patch_size = max(self.MIN_PATCH_SIZE, min(available_width // 4, self.MAX_PATCH_SIZE))
        for btn in self.options_buttons:
            btn.setFixedSize(patch_size, patch_size)
            btn.setIconSize(QSize(patch_size, patch_size))

        available_height = parent_widget.height()
        hole_height = int(max(self.MIN_HOLE_HEIGHT, min(available_height * 0.67, self.MAX_HOLE_HEIGHT)))
        complete_height = max(self.MIN_COMPLETE_HEIGHT, min(available_height * 0.85, self.MAX_COMPLETE_HEIGHT))

        if self.hole_label.isVisible():
            self.load_hole_image(hole_height)
        if self.complete_container and self.complete_container.isVisible():
            self.load_complete_image(complete_height)
        self.load_options_images()

        self.current_hole_height = hole_height

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

    def go_to_next_level_or_hall(self):
        if self.level < self.total_levels:
            self.parent.show_level(self.hall_name, self.level + 1)

    def go_to_next_hall(self):
        next_hall = get_next_hall(self.hall_name)
        if next_hall:
            self.parent.show_level(next_hall, 1)
        else:
            self.parent.show_hall_selection_from_level()
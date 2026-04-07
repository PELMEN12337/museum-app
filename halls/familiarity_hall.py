import random
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
from .base_hall import BaseHallLevel
from constants import get_next_hall

class FamiliarityHallLevel(BaseHallLevel):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        self.option_buttons = []
        self.sample_label = None
        self.current_sample_idx = None
        self.current_options = []
        self.correct_option_idx = None
        self.original_paths = []
        self.sample_path = None
        super().__init__(parent, hall_name, level, total_levels, preset_data)

    def setup_content(self):
        if not self.preset_data:
            label = QLabel(f"Уровень {self.level}: найдите такую же картинку")
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)
            return

        level_index = self.level - 1
        self.original_paths = self.preset_data["levels"][level_index][:3]
        if len(self.original_paths) < 3:
            error_label = QLabel("Недостаточно изображений для этого уровня (нужно 3)")
            error_label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(error_label)
            return

        self.current_sample_idx = random.randint(0, 2)
        self.sample_path = self.original_paths[self.current_sample_idx]

        self.current_options = self.original_paths[:]
        random.shuffle(self.current_options)
        self.correct_option_idx = self.current_options.index(self.sample_path)

        main_layout = QVBoxLayout()
        self.content_layout.addLayout(main_layout)

        # Варианты ответов (3 кнопки) с рамкой как в первом зале
        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        for idx, img_path in enumerate(self.current_options):
            btn = QPushButton()
            btn.setFixedSize(200, 200)
            btn.setIconSize(QSize(200, 200))
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid gray;
                    border-radius: 5px;
                    background-color: white;
                }
                QPushButton:hover {
                    border: 2px solid #FFB74D;
                }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.check_answer(i))
            options_layout.addWidget(btn)
            self.option_buttons.append(btn)
        main_layout.addLayout(options_layout)

        # Образец (найти такую же) – оставляем оранжевую рамку
        sample_layout = QVBoxLayout()
        sample_label = QLabel("Найди такую же картинку:")
        sample_label.setAlignment(Qt.AlignCenter)
        sample_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        sample_layout.addWidget(sample_label)

        self.sample_label = QLabel()
        self.sample_label.setAlignment(Qt.AlignCenter)
        self.sample_label.setStyleSheet("border: 2px solid #FFB74D; border-radius: 10px; background-color: #FFF8E7;")
        self.sample_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sample_layout.addWidget(self.sample_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(sample_layout)

        self.load_images()

        if self.level == self.total_levels:
            self.next_hall_btn = QPushButton("➡️ Перейти к следующему залу")
            self.next_hall_btn.clicked.connect(self.go_to_next_hall)
            self.next_hall_btn.setVisible(False)
            self.layout.addWidget(self.next_hall_btn, alignment=Qt.AlignCenter)

    def load_images(self):
        for btn, img_path in zip(self.option_buttons, self.current_options):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(btn.width(), btn.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                btn.setIcon(QIcon(scaled))
                btn.setIconSize(btn.size())
            else:
                btn.setText("Ошибка")

        if self.sample_path:
            pixmap = QPixmap(self.sample_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.sample_label.width(), self.sample_label.height(),
                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.sample_label.setPixmap(scaled)
            else:
                self.sample_label.setText("Ошибка")

    def update_sizes(self):
        if not self.option_buttons:
            return
        parent_widget = self.content_widget
        if not parent_widget:
            return
        # Доступная ширина (с учётом отступов по краям)
        available_width = parent_widget.width() - 60
        spacing = 20
        # Ширина каждой кнопки
        btn_width = (available_width - spacing * 2) // 3
        btn_height = btn_width  # квадратные
        # Увеличиваем ограничение по высоте: теперь не более половины высоты контента (вместо трети)
        btn_height = min(btn_height, parent_widget.height() // 2)

        for btn in self.option_buttons:
            btn.setFixedSize(btn_width, btn_height)
            btn.setIconSize(QSize(btn_width, btn_height))

        sample_size = int(btn_width * 0.5)
        self.sample_label.setFixedSize(sample_size, sample_size)
        self.load_images()

    def resizeEvent(self, event):
        self.update_sizes()
        super().resizeEvent(event)

    def showEvent(self, event):
        self.update_sizes()
        super().showEvent(event)

    def check_answer(self, selected_idx):
        if selected_idx == self.correct_option_idx:
            self.show_custom_message("Правильно!", "green")
            if self.level < self.total_levels:
                self.parent.show_level(self.hall_name, self.level + 1)
            else:
                if hasattr(self, 'next_hall_btn') and self.next_hall_btn:
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
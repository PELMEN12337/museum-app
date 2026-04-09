import os
import random
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QSizePolicy, QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
from .base_hall import BaseHallLevel
from constants import get_next_hall

class KeeperHallLevel(BaseHallLevel):
    def __init__(self, parent, hall_name, level, total_levels, preset_data=None):
        self.collections = []
        self.current_image_index = 0
        self.all_images = []
        self.category_of_image = []
        self.collection_buttons = []
        self.current_image_label = None
        self.result_labels = []          # QLabel для счётчиков (всегда видны, меняется текст)
        self.counter_values = []         # текущие значения счётчиков
        self.counters_visible = False    # общий флаг видимости текста счётчиков (изначально скрыты)
        self.toggle_counters_btn = None
        self.next_button = None
        self.next_hall_btn = None
        self.answer_given = False
        self.collection_widgets = []     # для хранения (layout, images)
        super().__init__(parent, hall_name, level, total_levels, preset_data)

    def setup_content(self):
        if not self.preset_data:
            label = QLabel(f"Уровень {self.level}: рассортируйте предметы по коллекциям")
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)
            return

        level_index = self.level - 1
        level_info = self.preset_data["levels"][level_index]
        self.collections = level_info["collections"]

        # Собираем плоский список всех изображений
        self.all_images = []
        self.category_of_image = []
        for cat_idx, col in enumerate(self.collections):
            for img_path in col["images"]:
                if img_path and os.path.exists(img_path):
                    self.all_images.append(img_path)
                    self.category_of_image.append(cat_idx)
        combined = list(zip(self.all_images, self.category_of_image))
        random.shuffle(combined)
        self.all_images, self.category_of_image = zip(*combined) if combined else ([], [])
        self.all_images = list(self.all_images)
        self.category_of_image = list(self.category_of_image)

        # Инициализируем счётчики
        self.counter_values = [0] * len(self.collections)

        main_layout = QVBoxLayout()
        self.content_layout.addLayout(main_layout)

        # Верхняя панель с кнопкой управления счётчиками
        top_panel = QHBoxLayout()
        self.toggle_counters_btn = QPushButton("📊 Показать счётчики")
        self.toggle_counters_btn.setStyleSheet("font-size: 14px; padding: 5px;")
        self.toggle_counters_btn.clicked.connect(self.toggle_all_counters)
        top_panel.addStretch()
        top_panel.addWidget(self.toggle_counters_btn)
        top_panel.addStretch()
        main_layout.addLayout(top_panel)

        # Контейнер для коллекций
        collections_layout = QHBoxLayout()
        collections_layout.setSpacing(60)
        for idx, col in enumerate(self.collections):
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setSpacing(5)
            container_layout.setContentsMargins(0, 0, 0, 0)

            # Название коллекции
            name_label = QLabel(col["name"])
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("font-weight: bold; font-size: 40px; margin: 0px; padding: 0px;")
            container_layout.addWidget(name_label)

            # Кнопка "Собрать сюда"
            btn = QPushButton("📥 Собрать сюда")
            btn.setStyleSheet("border-radius: 15px; font-size: 16px; padding: 10px; margin: 5px; border-radius: 10px;")
            btn.clicked.connect(lambda checked, i=idx: self.choose_collection(i))
            container_layout.addWidget(btn)

            # Счётчик (текст будет меняться, но виджет всегда видим)
            count_label = QLabel("")   # изначально пусто
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 0px; padding: 0px;")
            container_layout.addWidget(count_label)
            self.result_labels.append(count_label)

            # Место для миниатюр (появятся после завершения)
            thumbnails_layout = QGridLayout()
            thumbnails_layout.setSpacing(5)
            container_layout.addLayout(thumbnails_layout)

            collections_layout.addWidget(container)
            self.collection_buttons.append(btn)
            self.collection_widgets.append((thumbnails_layout, col["images"]))

        main_layout.addLayout(collections_layout)

        # Центральная картинка
        self.current_image_label = QLabel()
        self.current_image_label.setAlignment(Qt.AlignCenter)
        self.current_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_image_label.setStyleSheet("border: 3px solid #FFB74D; border-radius: 15px; background-color: #FFF8E7;")
        main_layout.addWidget(self.current_image_label, alignment=Qt.AlignCenter)

        # Кнопка "Далее"
        self.next_button = QPushButton("➡️ Далее")
        self.next_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.next_button.clicked.connect(self.go_to_next_level_or_hall)
        self.next_button.hide()
        main_layout.addWidget(self.next_button, alignment=Qt.AlignCenter)

        if self.level == self.total_levels:
            self.next_hall_btn = QPushButton("➡️ Перейти к следующему залу")
            self.next_hall_btn.setStyleSheet("font-size: 18px; padding: 10px;")
            self.next_hall_btn.clicked.connect(self.go_to_next_hall)
            self.next_hall_btn.hide()
            self.layout.addWidget(self.next_hall_btn, alignment=Qt.AlignCenter)

        self.update_sizes()

    def toggle_all_counters(self):
        """Показывает или скрывает текст счётчиков (без изменения layout)."""
        self.counters_visible = not self.counters_visible
        for idx, label in enumerate(self.result_labels):
            if self.counters_visible:
                total = len(self.collections[idx]['images'])
                current = self.counter_values[idx]
                label.setText(f"{current} / {total}")
            else:
                label.setText("")
        if self.counters_visible:
            self.toggle_counters_btn.setText("📊 Скрыть счётчики")
        else:
            self.toggle_counters_btn.setText("📊 Показать счётчики")

    def update_counter(self, idx, new_value):
        """Обновляет значение счётчика и отображает, если видимость включена."""
        self.counter_values[idx] = new_value
        if self.counters_visible:
            total = len(self.collections[idx]['images'])
            self.result_labels[idx].setText(f"{new_value} / {total}")

    def load_current_image(self):
        if self.current_image_index < len(self.all_images):
            self.update_sizes()
        else:
            # Все картинки распределены – показываем миниатюры и кнопку далее
            self.current_image_label.hide()
            for btn in self.collection_buttons:
                btn.setEnabled(False)
            # Показываем миниатюры собранных предметов
            for idx, (layout, images) in enumerate(self.collection_widgets):
                # Очищаем layout
                for i in reversed(range(layout.count())):
                    widget = layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                # Добавляем до 3 миниатюр
                for img_idx, img_path in enumerate(images[:3]):
                    if os.path.exists(img_path):
                        pixmap = QPixmap(img_path)
                        if not pixmap.isNull():
                            scaled = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            label = QLabel()
                            label.setPixmap(scaled)
                            label.setFixedSize(100, 100)
                            label.setAlignment(Qt.AlignCenter)
                            label.setStyleSheet("border: 1px solid #FFB74D; border-radius: 5px; background-color: white;")
                            layout.addWidget(label, 0, img_idx)
            if self.level == self.total_levels:
                if self.next_hall_btn:
                    self.next_hall_btn.show()
            else:
                self.next_button.show()

    def choose_collection(self, cat_idx):
        if self.answer_given:
            return
        if self.current_image_index < len(self.category_of_image):
            correct_cat = self.category_of_image[self.current_image_index]
            if cat_idx == correct_cat:
                self.show_custom_message("Правильно!", "green")
                new_count = self.counter_values[cat_idx] + 1
                self.update_counter(cat_idx, new_count)
                self.current_image_index += 1
                self.load_current_image()
            else:
                self.show_custom_message("Попробуйте ещё раз!", "red")
        else:
            pass

    def update_sizes(self):
        if not self.current_image_label:
            return
        parent_widget = self.content_widget
        if not parent_widget:
            return
        available_width = parent_widget.width() - 60
        available_height = parent_widget.height() - 250
        img_size = min(available_width * 8 // 10, available_height, 850)
        self.current_image_label.setFixedSize(img_size, img_size)
        if self.current_image_index < len(self.all_images):
            pixmap = QPixmap(self.all_images[self.current_image_index])
            if not pixmap.isNull():
                scaled = pixmap.scaled(img_size, img_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.current_image_label.setPixmap(scaled)

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
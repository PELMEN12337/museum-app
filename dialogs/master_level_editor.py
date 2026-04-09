import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFileDialog, QTabWidget, QMessageBox, QWidget, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

# ----------------------------------------------------------------------
# Специальный редактор для зала мастера
# ----------------------------------------------------------------------
class MasterLevelEditorDialog(QDialog):
    def __init__(self, hall_name, levels_data, parent=None):
        super().__init__(parent)
        self.hall_name = hall_name
        self.levels_data = levels_data
        self.setWindowTitle(f"Редактор уровней – {hall_name}")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; }
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 8px; background-color: white; }
            QTabBar::tab { background-color: #E0E0E0; border-radius: 6px; padding: 6px 12px; margin: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #FFB74D; color: white; }
            QPushButton { background-color: #FFB74D; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #FFA726; }
        """)

        layout = QVBoxLayout(self)
        main_layout = QVBoxLayout()
        layout.addLayout(main_layout)

        title = QLabel(f"🖼️ Настройка зала: {hall_name}")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Кнопки добавления/удаления уровней
        levels_btn_layout = QHBoxLayout()
        self.add_level_btn = QPushButton("➕ Добавить уровень")
        self.add_level_btn.clicked.connect(self.add_level)
        self.remove_level_btn = QPushButton("➖ Удалить последний уровень")
        self.remove_level_btn.clicked.connect(self.remove_level)
        levels_btn_layout.addStretch()
        levels_btn_layout.addWidget(self.add_level_btn)
        levels_btn_layout.addWidget(self.remove_level_btn)
        levels_btn_layout.addStretch()
        main_layout.addLayout(levels_btn_layout)

        self.level_tabs = QTabWidget()
        main_layout.addWidget(self.level_tabs)

        self.tab_data = []

        # Если нет уровней, показываем сообщение
        if not self.levels_data:
            self._show_empty_message()
        else:
            for i, level_info in enumerate(self.levels_data):
                self._add_level_tab(i, level_info)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("💾 Сохранить уровни")
        self.cancel_btn = QPushButton("❌ Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

    def _show_empty_message(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        label = QLabel("Нет уровней. Нажмите «Добавить уровень»")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")
        empty_layout.addWidget(label)
        self.level_tabs.addTab(empty_widget, "Нет уровней")

    def _add_level_tab(self, level_idx, level_info):
        # Если есть сообщение о пустоте, удаляем его
        if self.level_tabs.count() == 1 and self.level_tabs.tabText(0) == "Нет уровней":
            self.level_tabs.clear()

        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Основная картинка
        tab_layout.addWidget(QLabel("Основная картинка (узор):"))
        main_btn = QPushButton("Загрузить основную картинку")
        main_btn.clicked.connect(lambda checked, idx=level_idx: self.load_main_image(idx))
        tab_layout.addWidget(main_btn)
        main_preview = QLabel()
        main_preview.setFixedSize(200, 200)
        main_preview.setAlignment(Qt.AlignCenter)
        main_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
        tab_layout.addWidget(main_preview)

        # Подсказка для цветов
        hint_label = QLabel("🖱️ ЛКМ – выбрать правильные цвета (зелёная рамка)\n🗑️ ПКМ – удалить цвет")
        hint_label.setStyleSheet("color: #555; font-size: 11px;")
        tab_layout.addWidget(hint_label)

        # Цвета
        tab_layout.addWidget(QLabel("Цвета (нужно 8 изображений):"))
        load_colors_btn = QPushButton("📂 Загрузить цвета (дополнить пустые)")
        load_colors_btn.clicked.connect(lambda checked, idx=level_idx: self.add_color_images(idx))
        tab_layout.addWidget(load_colors_btn)

        # Счетчик загруженных цветов
        colors_counter = QLabel("Загружено цветов: 0 / 8")
        colors_counter.setStyleSheet("color: red; font-weight: bold;")
        tab_layout.addWidget(colors_counter)

        # Сетка для миниатюр цветов
        colors_grid = QGridLayout()
        color_labels = []
        color_widgets = []
        for j in range(8):
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel()
            label.setFixedSize(100, 100)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
            label.mousePressEvent = lambda event, idx=level_idx, pos=j: self.on_color_click(event, idx, pos)
            name_label = QLabel(f"Цвет {j+1}")
            name_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(label)
            container_layout.addWidget(name_label)
            colors_grid.addWidget(container, j//4, j%4)
            color_labels.append(label)
            color_widgets.append(container)
        tab_layout.addLayout(colors_grid)

        self.level_tabs.addTab(tab, f"Уровень {level_idx+1}")
        self.tab_data.append({
            'level_idx': level_idx,
            'main_preview': main_preview,
            'color_labels': color_labels,
            'color_widgets': color_widgets,
            'colors_counter': colors_counter,
            'main_path': level_info.get("main_image", ""),
            'color_paths': level_info.get("color_images", [""]*8),
            'correct_indices': set(level_info.get("correct_indices", []))
        })
        self.update_tab_display(level_idx)

    def add_level(self):
        if self.level_tabs.count() == 1 and self.level_tabs.tabText(0) == "Нет уровней":
            self.level_tabs.clear()
            self.tab_data.clear()
            self.levels_data.clear()

        new_level = {"main_image": "", "color_images": [""]*8, "correct_indices": []}
        self.levels_data.append(new_level)
        self._add_level_tab(len(self.levels_data)-1, new_level)
        self.level_tabs.setCurrentIndex(self.level_tabs.count()-1)

    def remove_level(self):
        if len(self.levels_data) == 0:
            return
        self.levels_data.pop()
        self.tab_data.pop()
        self.level_tabs.removeTab(self.level_tabs.count()-1)
        if len(self.levels_data) == 0:
            self._show_empty_message()

    def load_main_image(self, level_idx):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите основную картинку", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.tab_data[level_idx]['main_path'] = file
            self.update_tab_display(level_idx)

    def add_color_images(self, level_idx):
        data = self.tab_data[level_idx]
        current_paths = data['color_paths'][:]
        empty_positions = [i for i, p in enumerate(current_paths) if not p or not os.path.exists(p)]
        if not empty_positions:
            QMessageBox.information(self, "Информация", "Все 8 цветов уже загружены. Чтобы загрузить новый цвет, сначала удалите какой-нибудь через ПКМ.")
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите изображения для добавления (дополнят пустые места)", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return
        for i, file in enumerate(files):
            if i >= len(empty_positions):
                QMessageBox.information(self, "Внимание", f"Свободно только {len(empty_positions)} мест, загружено {len(files)}. Лишние не добавлены.")
                break
            pos = empty_positions[i]
            current_paths[pos] = file
        data['color_paths'] = current_paths
        self.update_tab_display(level_idx)

    def on_color_click(self, event, level_idx, pos):
        if event.button() == Qt.LeftButton:
            self.toggle_correct(level_idx, pos)
        elif event.button() == Qt.RightButton:
            self.remove_color_image(level_idx, pos)

    def toggle_correct(self, level_idx, pos):
        if pos in self.tab_data[level_idx]['correct_indices']:
            self.tab_data[level_idx]['correct_indices'].remove(pos)
        else:
            self.tab_data[level_idx]['correct_indices'].add(pos)
        self.update_tab_display(level_idx)

    def remove_color_image(self, level_idx, pos):
        data = self.tab_data[level_idx]
        if data['color_paths'][pos] and os.path.exists(data['color_paths'][pos]):
            data['color_paths'][pos] = ""
            if pos in data['correct_indices']:
                data['correct_indices'].remove(pos)
            self.update_tab_display(level_idx)
        else:
            QMessageBox.information(self, "Удаление", "В этой позиции нет изображения.")

    def update_tab_display(self, level_idx):
        data = self.tab_data[level_idx]
        main_path = data['main_path']
        if main_path and os.path.exists(main_path):
            pixmap = QPixmap(main_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                data['main_preview'].setPixmap(scaled)
            else:
                data['main_preview'].setText("Ошибка")
        else:
            data['main_preview'].setText("Нет изображения")

        color_paths = data['color_paths']
        loaded_count = sum(1 for p in color_paths if p and os.path.exists(p))
        data['colors_counter'].setText(f"Загружено цветов: {loaded_count} / 8")
        if loaded_count == 8:
            data['colors_counter'].setStyleSheet("color: green; font-weight: bold;")
        else:
            data['colors_counter'].setStyleSheet("color: red; font-weight: bold;")

        for j, label in enumerate(data['color_labels']):
            path = color_paths[j] if j < len(color_paths) else ""
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    label.setPixmap(scaled)
                else:
                    label.setText("Ошибка")
            else:
                label.setText("Нет")
            if j in data['correct_indices']:
                label.setStyleSheet("border: 4px solid green; border-radius: 5px; background-color: #E8F5E9;")
            else:
                label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")

    def accept(self):
        for i, data in enumerate(self.tab_data):
            color_paths = data['color_paths']
            loaded_count = sum(1 for p in color_paths if p and os.path.exists(p))
            if loaded_count != 8:
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} загружено {loaded_count} цветов, нужно 8.")
                return
            if not data['main_path'] or not os.path.exists(data['main_path']):
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} не загружена основная картинка.")
                return
        for i, data in enumerate(self.tab_data):
            self.levels_data[i] = {
                "main_image": data['main_path'],
                "color_images": data['color_paths'],
                "correct_indices": list(data['correct_indices'])
            }
        super().accept()
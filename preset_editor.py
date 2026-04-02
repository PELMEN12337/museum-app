import os
import copy
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QTabWidget, QMessageBox,
                             QWidget, QScrollArea, QGridLayout, QApplication, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from constants import HALLS, ALL_HALLS

class PresetEditor(QDialog):
    def __init__(self, preset_manager, parent=None, preset_data=None, preset_index=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.preset_index = preset_index
        self.setWindowTitle("Редактор пресета" if preset_index is not None else "Создание пресета")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название пресета:"))
        self.preset_name = QLineEdit()
        layout.addWidget(self.preset_name)

        self.main_tabs = QTabWidget()
        layout.addWidget(self.main_tabs)

        self.tab_data = {}

        for hall_name in ALL_HALLS:
            levels = HALLS[hall_name]
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            tab_layout.addWidget(QLabel(f"Количество уровней: {levels}"))

            setup_btn = QPushButton(f"Настроить уровни для зала «{hall_name}»")
            setup_btn.clicked.connect(lambda checked, name=hall_name: self.setup_hall_levels(name))
            tab_layout.addWidget(setup_btn)

            level_combo = QComboBox()
            for lvl in range(1, levels + 1):
                level_combo.addItem(f"Уровень {lvl}")
            tab_layout.addWidget(level_combo)

            preview_scroll = QScrollArea()
            preview_scroll.setWidgetResizable(True)
            preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            preview_container = QWidget()
            preview_grid = QGridLayout(preview_container)
            preview_grid.setSpacing(5)
            preview_scroll.setWidget(preview_container)
            tab_layout.addWidget(preview_scroll)

            self.tab_data[hall_name] = {
                "level_data": None,
                "correct_answers": None,
                "level_combo": level_combo,
                "preview_grid": preview_grid,
                "preview_container": preview_container
            }

            def make_update_preview(hall):
                def update_preview(level_index):
                    grid = self.tab_data[hall]["preview_grid"]
                    for i in reversed(range(grid.count())):
                        widget = grid.itemAt(i).widget()
                        if widget:
                            widget.setParent(None)
                    level_data = self.tab_data[hall]["level_data"]
                    if level_data and level_index < len(level_data):
                        img_list = level_data[level_index]
                        for idx, img_path in enumerate(img_list):
                            if img_path and os.path.exists(img_path):
                                pixmap = QPixmap(img_path)
                                if not pixmap.isNull():
                                    label = QLabel()
                                    scaled = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                    label.setPixmap(scaled)
                                    label.setToolTip(os.path.basename(img_path))
                                    label.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px; background-color: white;")
                                    grid.addWidget(label, idx // 4, idx % 4)
                                else:
                                    error_label = QLabel("Ошибка загрузки")
                                    error_label.setStyleSheet("border: 1px solid red; background-color: #FFCCCC;")
                                    grid.addWidget(error_label, idx // 4, idx % 4)
                return update_preview

            level_combo.currentIndexChanged.connect(make_update_preview(hall_name))
            self.main_tabs.addTab(tab, hall_name)

        if preset_data:
            self.preset_name.setText(preset_data["name"])
            for hall_name, hall_data in preset_data["halls"].items():
                if hall_name in self.tab_data:
                    self.tab_data[hall_name]["level_data"] = copy.deepcopy(hall_data["levels"])
                    self.tab_data[hall_name]["correct_answers"] = copy.deepcopy(hall_data["correct_answers"])
                    combo = self.tab_data[hall_name]["level_combo"]
                    combo.setCurrentIndex(0)

        button_box = QHBoxLayout()
        self.ok_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_box.addStretch()
        button_box.addWidget(self.ok_btn)
        button_box.addWidget(self.cancel_btn)
        layout.addLayout(button_box)

    def setup_hall_levels(self, hall_name):
        levels = HALLS[hall_name]
        if self.tab_data[hall_name]["level_data"] is None:
            self.tab_data[hall_name]["level_data"] = [[] for _ in range(levels)]
            self.tab_data[hall_name]["correct_answers"] = [0] * levels

        level_data_copy = copy.deepcopy(self.tab_data[hall_name]["level_data"])
        correct_answers_copy = copy.deepcopy(self.tab_data[hall_name]["correct_answers"])

        for i in range(len(level_data_copy)):
            seen = set()
            unique = []
            for p in level_data_copy[i]:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            level_data_copy[i] = unique
            if correct_answers_copy[i] >= len(unique):
                correct_answers_copy[i] = 0 if unique else None

        editor = HallLevelEditorDialog(hall_name, levels, level_data_copy, correct_answers_copy, self)
        if editor.exec_():
            self.tab_data[hall_name]["level_data"] = level_data_copy
            self.tab_data[hall_name]["correct_answers"] = correct_answers_copy
            current_level = self.tab_data[hall_name]["level_combo"].currentIndex()
            self.tab_data[hall_name]["level_combo"].setCurrentIndex(current_level)

    def accept(self):
        if not self.preset_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название пресета.")
            return

        any_configured = False
        for hall_name, data in self.tab_data.items():
            if data["level_data"] is not None:
                any_configured = True
                for i, images in enumerate(data["level_data"]):
                    if not images:
                        QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит изображений.")
                        return
        if not any_configured:
            QMessageBox.warning(self, "Ошибка", "Не настроен ни один зал. Добавьте изображения хотя бы для одного зала.")
            return

        halls_data = {}
        for hall_name, data in self.tab_data.items():
            if data["level_data"] is not None:
                halls_data[hall_name] = {
                    "levels": data["level_data"],
                    "correct_answers": data["correct_answers"]
                }

        preset = {
            "name": self.preset_name.text().strip(),
            "halls": halls_data
        }

        for hall_name, hall_data in halls_data.items():
            for level_idx, img_list in enumerate(hall_data["levels"]):
                new_paths = self.preset_manager.copy_images_to_preset(
                    preset["name"], hall_name, level_idx+1, img_list
                )
                hall_data["levels"][level_idx] = new_paths

        if self.preset_index is None:
            self.preset_manager.add_preset(preset)
        else:
            self.preset_manager.presets[self.preset_index] = preset
            self.preset_manager.save_presets()

        super().accept()


class HallLevelEditorDialog(QDialog):
    def __init__(self, hall_name, total_levels, level_data, correct_answers, parent=None):
        super().__init__(parent)
        self.hall_name = hall_name
        self.total_levels = total_levels
        self.level_data = level_data
        self.correct_answers = correct_answers
        self.setWindowTitle(f"Редактор уровней – {hall_name}")
        self.setMinimumSize(800, 600)

        main_layout = QVBoxLayout(self)

        self.level_tabs = QTabWidget()
        main_layout.addWidget(self.level_tabs)

        self.tab_widgets = []
        for i in range(total_levels):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            container = QWidget()
            grid_layout = QGridLayout(container)
            grid_layout.setSpacing(10)
            scroll.setWidget(container)
            tab_layout.addWidget(scroll)

            add_btn = QPushButton("Добавить изображения")
            add_btn.clicked.connect(lambda checked, idx=i: self.add_images(idx))
            tab_layout.addWidget(add_btn)

            delete_btn = QPushButton("Удалить выбранное")
            delete_btn.clicked.connect(lambda checked, idx=i: self.delete_selected(idx))
            tab_layout.addWidget(delete_btn)

            self.level_tabs.addTab(tab, f"Уровень {i+1}")
            self.tab_widgets.append({
                'grid': grid_layout,
                'images': [],
                'selected_label': None,
                'level_idx': i
            })

            valid_paths = []
            for img_path in level_data[i]:
                if img_path and os.path.exists(img_path):
                    self._display_image(i, img_path)
                    valid_paths.append(img_path)
                else:
                    print(f"File not found: {img_path}")
            self.level_data[i] = valid_paths

            if correct_answers[i] is not None and 0 <= correct_answers[i] < len(valid_paths):
                self.select_image(i, correct_answers[i])
            elif valid_paths:
                self.select_image(i, 0)
                self.correct_answers[i] = 0
            else:
                self.correct_answers[i] = None

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Сохранить уровни")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

    def _display_image(self, level_idx, file_path):
        tab = self.tab_widgets[level_idx]
        grid = tab['grid']
        row = len(tab['images']) // 3
        col = len(tab['images']) % 3

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled)
            label.setFixedSize(150, 150)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid gray; border-radius: 5px; padding: 2px; background-color: white;")
            label.setToolTip(os.path.basename(file_path))
        else:
            label.setText("Ошибка загрузки")
            label.setFixedSize(150, 150)

        name_label = QLabel(os.path.basename(file_path))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)

        container_layout.addWidget(label)
        container_layout.addWidget(name_label)

        tab['images'].append((container, label, file_path))
        grid.addWidget(container, row, col)

        label.mousePressEvent = lambda event, idx=len(tab['images'])-1: self.on_image_click(level_idx, idx)

    def add_images(self, level_idx):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите изображения", "",
                                                "Images (*.png *.jpg *.jpeg *.bmp)")
        for file in files:
            self.add_image_to_tab(level_idx, file)
            QApplication.processEvents()

    def add_image_to_tab(self, level_idx, file_path):
        tab = self.tab_widgets[level_idx]
        grid = tab['grid']
        row = len(tab['images']) // 3
        col = len(tab['images']) % 3

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled)
            label.setFixedSize(150, 150)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid gray; border-radius: 5px; padding: 2px; background-color: white;")
            label.setToolTip(os.path.basename(file_path))
        else:
            label.setText("Ошибка загрузки")
            label.setFixedSize(150, 150)

        name_label = QLabel(os.path.basename(file_path))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)

        container_layout.addWidget(label)
        container_layout.addWidget(name_label)

        tab['images'].append((container, label, file_path))
        grid.addWidget(container, row, col)

        label.mousePressEvent = lambda event, idx=len(tab['images'])-1: self.on_image_click(level_idx, idx)

        self.level_data[level_idx].append(file_path)

        if len(tab['images']) == 1:
            self.select_image(level_idx, 0)

    def on_image_click(self, level_idx, image_idx):
        self.select_image(level_idx, image_idx)

    def select_image(self, level_idx, image_idx):
        tab = self.tab_widgets[level_idx]
        if tab['selected_label']:
            tab['selected_label'].setStyleSheet("border: 2px solid gray; border-radius: 5px; padding: 2px; background-color: white;")
        new_label = tab['images'][image_idx][1]
        new_label.setStyleSheet("border: 3px solid green; border-radius: 5px; padding: 2px; background-color: #E8F5E9;")
        tab['selected_label'] = new_label
        self.correct_answers[level_idx] = image_idx

    def delete_selected(self, level_idx):
        tab = self.tab_widgets[level_idx]
        if tab['selected_label'] is None:
            QMessageBox.information(self, "Удаление", "Сначала выберите изображение для удаления (кликните на него).")
            return
        selected_idx = None
        for i, (container, label, path) in enumerate(tab['images']):
            if label == tab['selected_label']:
                selected_idx = i
                break
        if selected_idx is None:
            return

        container, _, _ = tab['images'][selected_idx]
        grid = tab['grid']
        grid.removeWidget(container)
        container.deleteLater()

        del tab['images'][selected_idx]
        del self.level_data[level_idx][selected_idx]

        if selected_idx == self.correct_answers[level_idx]:
            if tab['images']:
                self.select_image(level_idx, 0)
            else:
                self.correct_answers[level_idx] = None
                tab['selected_label'] = None
        elif selected_idx < self.correct_answers[level_idx]:
            self.correct_answers[level_idx] -= 1

        self.rebuild_grid(level_idx)

    def rebuild_grid(self, level_idx):
        tab = self.tab_widgets[level_idx]
        grid = tab['grid']
        for i in reversed(range(grid.count())):
            widget = grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for idx, (container, _, _) in enumerate(tab['images']):
            row = idx // 3
            col = idx % 3
            grid.addWidget(container, row, col)

    def accept(self):
        for i, ans in enumerate(self.correct_answers):
            if ans is None or ans < 0 or ans >= len(self.level_data[i]):
                QMessageBox.warning(self, "Ошибка",
                                    f"Для уровня {i+1} выберите правильный ответ (кликните на изображение).")
                return
        super().accept()
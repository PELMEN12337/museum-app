import os
import copy
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QTabWidget, QMessageBox,
                             QWidget, QScrollArea, QGridLayout, QApplication, QComboBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from constants import ALL_HALLS, HALLS

class PresetEditor(QDialog):
    def __init__(self, preset_manager, parent=None, preset_data=None, preset_index=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.preset_index = preset_index
        self.setWindowTitle("Редактор пресета" if preset_index is not None else "Создание пресета")
        self.setMinimumSize(900, 700)
        self.resize(1230, 800)
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QTabWidget::pane {
                border: 1px solid #DDD;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                border-radius: 6px;
                padding: 8px 4px;
                margin: 2px;
                font-weight: bold;
                padding: 6px;
            }
            QTabBar::tab:selected {
                background-color: #FFB74D;
                color: white;
            }
            QPushButton {
                background-color: #FFB74D;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                color: #5D3A1A;
            }
            QPushButton:hover {
                background-color: #FFA726;
            }
            QPushButton:pressed {
                background-color: #F57C00;
            }
            QLineEdit {
                border: 1px solid #CCC;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
            QLabel {
                font-size: 13px;
                color: #333;
            }
            QComboBox {
                border: 1px solid #CCC;
                border-radius: 6px;
                padding: 4px;
                background-color: white;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📝 Настройка пресета")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название пресета:"))
        self.preset_name = QLineEdit()
        self.preset_name.setMinimumWidth(300)
        name_layout.addWidget(self.preset_name)
        name_layout.addStretch()
        main_layout.addLayout(name_layout)

        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabBar::tab {
                font-size: 11px;
                padding: 6px 8px;
                margin: 2px;
                min-width: 200px;
            }
        """)
        self.main_tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.main_tabs, 1)

        self.tab_data = {}

        for hall_name in ALL_HALLS:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setSpacing(15)

            setup_btn = QPushButton(f"🎨 Настроить уровни для зала «{hall_name}»")
            setup_btn.setMinimumHeight(40)
            setup_btn.clicked.connect(lambda checked, name=hall_name: self.setup_hall_levels(name))
            tab_layout.addWidget(setup_btn)

            preview_label = QLabel("Предпросмотр уровня:")
            preview_label.setFont(QFont("Arial", 12, QFont.Bold))
            tab_layout.addWidget(preview_label)
            level_combo = QComboBox()
            tab_layout.addWidget(level_combo)

            preview_scroll = QScrollArea()
            preview_scroll.setWidgetResizable(True)
            preview_scroll.setMinimumHeight(200)
            preview_container = QWidget()
            preview_grid = QGridLayout(preview_container)
            preview_grid.setSpacing(10)
            preview_scroll.setWidget(preview_container)
            tab_layout.addWidget(preview_scroll, 1)

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
                        w = grid.itemAt(i).widget()
                        if w:
                            w.setParent(None)
                    level_data = self.tab_data[hall]["level_data"]
                    if level_data and level_index < len(level_data):
                        for idx, img_path in enumerate(level_data[level_index]):
                            if img_path and os.path.exists(img_path):
                                pixmap = QPixmap(img_path)
                                if not pixmap.isNull():
                                    label = QLabel()
                                    scaled = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                    label.setPixmap(scaled)
                                    label.setToolTip(os.path.basename(img_path))
                                    label.setStyleSheet("border: 1px solid #AAA; border-radius: 5px; padding: 2px; background: white;")
                                    grid.addWidget(label, idx // 4, idx % 4)
                return update_preview

            level_combo.currentIndexChanged.connect(make_update_preview(hall_name))
            self.main_tabs.addTab(tab, hall_name)

        if preset_data:
            self.preset_name.setText(preset_data["name"])
            for hall_name, hall_data in preset_data["halls"].items():
                if hall_name in self.tab_data:
                    self.tab_data[hall_name]["level_data"] = copy.deepcopy(hall_data["levels"])
                    self.tab_data[hall_name]["correct_answers"] = copy.deepcopy(hall_data["correct_answers"])
                    self._update_preview_combo(hall_name)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("✅ Сохранить пресет")
        self.ok_btn.setMinimumWidth(150)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumWidth(150)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def _update_preview_combo(self, hall_name):
        data = self.tab_data[hall_name]
        combo = data["level_combo"]
        combo.clear()
        if data["level_data"]:
            for i in range(len(data["level_data"])):
                combo.addItem(f"Уровень {i+1}")
            combo.setCurrentIndex(0)

    def setup_hall_levels(self, hall_name):
        data = self.tab_data[hall_name]
        if data["level_data"] is None:
            default_levels = 1
            data["level_data"] = [[] for _ in range(default_levels)]
            data["correct_answers"] = [0] * default_levels

        level_data_copy = copy.deepcopy(data["level_data"])
        correct_answers_copy = copy.deepcopy(data["correct_answers"])

        editor = HallLevelEditorDialog(hall_name, level_data_copy, correct_answers_copy, self)
        if editor.exec_():
            data["level_data"] = level_data_copy
            data["correct_answers"] = correct_answers_copy
            self._update_preview_combo(hall_name)

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
    def __init__(self, hall_name, level_data, correct_answers, parent=None):
        super().__init__(parent)
        self.hall_name = hall_name
        self.level_data = level_data
        self.correct_answers = correct_answers
        self.setWindowTitle(f"Редактор уровней – {hall_name}")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QTabWidget::pane {
                border: 1px solid #DDD;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #FFB74D;
                color: white;
            }
            QPushButton {
                background-color: #FFB74D;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFA726; }
            QPushButton:pressed { background-color: #F57C00; }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel {
                font-size: 13px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"🖼️ Настройка зала: {hall_name}")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        levels_btn_layout = QHBoxLayout()
        self.add_level_btn = QPushButton("➕ Добавить уровень")
        self.add_level_btn.setMinimumWidth(150)
        self.add_level_btn.clicked.connect(self.add_level)
        self.remove_level_btn = QPushButton("➖ Удалить последний уровень")
        self.remove_level_btn.setMinimumWidth(200)
        self.remove_level_btn.clicked.connect(self.remove_level)
        levels_btn_layout.addStretch()
        levels_btn_layout.addWidget(self.add_level_btn)
        levels_btn_layout.addWidget(self.remove_level_btn)
        levels_btn_layout.addStretch()
        main_layout.addLayout(levels_btn_layout)

        self.level_tabs = QTabWidget()
        self.level_tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.level_tabs, 1)

        self.tab_widgets = []
        self.rebuild_tabs()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("💾 Сохранить уровни")
        self.ok_btn.setMinimumWidth(150)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumWidth(150)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def rebuild_tabs(self):
        self.level_tabs.clear()
        self.tab_widgets.clear()
        for i in range(len(self.level_data)):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setSpacing(10)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            container = QWidget()
            grid_layout = QGridLayout(container)
            grid_layout.setSpacing(15)
            scroll.setWidget(container)
            tab_layout.addWidget(scroll, 1)

            btn_row = QHBoxLayout()
            add_img_btn = QPushButton("📂 Добавить изображения")
            add_img_btn.clicked.connect(lambda checked, idx=i: self.add_images(idx))
            delete_img_btn = QPushButton("🗑️ Удалить выбранное")
            delete_img_btn.clicked.connect(lambda checked, idx=i: self.delete_selected(idx))
            btn_row.addStretch()
            btn_row.addWidget(add_img_btn)
            btn_row.addWidget(delete_img_btn)
            btn_row.addStretch()
            tab_layout.addLayout(btn_row)

            self.level_tabs.addTab(tab, f"Уровень {i+1}")
            self.tab_widgets.append({
                'grid': grid_layout,
                'images': [],
                'selected_label': None,
                'level_idx': i
            })

            valid_paths = []
            for img_path in self.level_data[i]:
                if img_path and os.path.exists(img_path):
                    self._display_image(i, img_path)
                    valid_paths.append(img_path)
                else:
                    print(f"File not found: {img_path}")
            self.level_data[i] = valid_paths

            if i < len(self.correct_answers) and self.correct_answers[i] is not None and 0 <= self.correct_answers[i] < len(valid_paths):
                self.select_image(i, self.correct_answers[i])
            elif valid_paths:
                self.select_image(i, 0)
                self.correct_answers[i] = 0
            else:
                self.correct_answers[i] = None

    def add_level(self):
        self.level_data.append([])
        self.correct_answers.append(0)
        self.rebuild_tabs()
        self.level_tabs.setCurrentIndex(len(self.level_data)-1)

    def remove_level(self):
        if len(self.level_data) <= 1:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить последний уровень.")
            return
        self.level_data.pop()
        self.correct_answers.pop()
        self.rebuild_tabs()

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
            label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
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
            label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
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
            tab['selected_label'].setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
        new_label = tab['images'][image_idx][1]
        new_label.setStyleSheet("border: 3px solid green; border-radius: 5px; background-color: #E8F5E9;")
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
            w = grid.itemAt(i).widget()
            if w:
                w.setParent(None)
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
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFileDialog, QTabWidget, QMessageBox, QWidget, QGroupBox,
                             QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class RestorerLevelEditorDialog(QDialog):
    def __init__(self, hall_name, levels_data, parent=None):
        super().__init__(parent)
        self.hall_name = hall_name
        self.levels_data = levels_data
        self.setWindowTitle(f"Редактор уровней – {hall_name}")
        self.setMinimumSize(700, 800)
        self.resize(900, 950)
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; }
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 8px; background-color: white; }
            QTabBar::tab { background-color: #E0E0E0; border-radius: 6px; padding: 6px 12px; margin: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #FFB74D; color: white; }
            QPushButton { background-color: #FFB74D; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #FFA726; }
            QScrollArea { border: none; background-color: transparent; }
            QLabel { font-size: 12px; }
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
        tab_layout.setSpacing(15)

        # Целая картинка
        complete_group = QGroupBox("Целая картинка (без дефекта)")
        complete_layout = QVBoxLayout(complete_group)
        complete_btn = QPushButton("📂 Загрузить целую картинку")
        complete_btn.clicked.connect(lambda checked, idx=level_idx: self.load_complete_image(idx))
        complete_layout.addWidget(complete_btn)
        complete_preview = QLabel()
        complete_preview.setFixedSize(170, 170)
        complete_preview.setAlignment(Qt.AlignCenter)
        complete_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
        complete_preview.setContextMenuPolicy(Qt.CustomContextMenu)
        complete_preview.customContextMenuRequested.connect(lambda pos, idx=level_idx: self.delete_image(idx, "complete"))
        complete_layout.addWidget(complete_preview, alignment=Qt.AlignCenter)
        tab_layout.addWidget(complete_group)

        # Картинка с дыркой
        hole_group = QGroupBox("Картинка с дыркой")
        hole_layout = QVBoxLayout(hole_group)
        hole_btn = QPushButton("📂 Загрузить картинку с дыркой")
        hole_btn.clicked.connect(lambda checked, idx=level_idx: self.load_hole_image(idx))
        hole_layout.addWidget(hole_btn)
        hole_preview = QLabel()
        hole_preview.setFixedSize(170, 170)
        hole_preview.setAlignment(Qt.AlignCenter)
        hole_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
        hole_preview.setContextMenuPolicy(Qt.CustomContextMenu)
        hole_preview.customContextMenuRequested.connect(lambda pos, idx=level_idx: self.delete_image(idx, "hole"))
        hole_layout.addWidget(hole_preview, alignment=Qt.AlignCenter)
        tab_layout.addWidget(hole_group)

        # Заплатки (3 штуки)
        patches_group = QGroupBox("Заплатки (3 изображения) – клик ЛКМ – выбрать правильную, ПКМ – удалить")
        patches_layout = QVBoxLayout(patches_group)
        patches_btn = QPushButton("📂 Загрузить заплатки (дополнят пустые места)")
        patches_btn.clicked.connect(lambda checked, idx=level_idx: self.load_patches_bulk(idx))
        patches_layout.addWidget(patches_btn)

        patches_grid = QGridLayout()
        patches_grid.setSpacing(20)
        patch_previews = []
        for j in range(3):
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel()
            label.setFixedSize(120, 120)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
            label.setContextMenuPolicy(Qt.CustomContextMenu)
            label.customContextMenuRequested.connect(lambda pos, idx=level_idx, pos_idx=j: self.delete_patch(idx, pos_idx))
            label.mousePressEvent = lambda event, idx=level_idx, pos=j: self.set_correct_patch(idx, pos) if event.button() == Qt.LeftButton else None
            name_label = QLabel(f"Заплатка {j+1}")
            name_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(label)
            container_layout.addWidget(name_label)
            patches_grid.addWidget(container, 0, j)
            patch_previews.append(label)
        patches_layout.addLayout(patches_grid)
        tab_layout.addWidget(patches_group)

        # Отображение текущей правильной заплатки
        correct_info = QLabel("Правильная заплатка: не выбрана")
        correct_info.setStyleSheet("font-weight: bold; color: green;")
        tab_layout.addWidget(correct_info)

        self.level_tabs.addTab(tab, f"Уровень {level_idx+1}")
        self.tab_data.append({
            'level_idx': level_idx,
            'complete_preview': complete_preview,
            'hole_preview': hole_preview,
            'patch_previews': patch_previews,
            'correct_info': correct_info,
            'complete_path': level_info.get("complete_image", ""),
            'hole_path': level_info.get("hole_image", ""),
            'patches_paths': level_info.get("patches", [""]*3),
            'correct_patch_idx': level_info.get("correct_patch_idx", None)
        })
        self.update_tab_display(level_idx)

    def add_level(self):
        if self.level_tabs.count() == 1 and self.level_tabs.tabText(0) == "Нет уровней":
            self.level_tabs.clear()
            self.tab_data.clear()
            self.levels_data.clear()

        new_level = {"complete_image": "", "hole_image": "", "patches": [""]*3, "correct_patch_idx": 0}
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

    def load_complete_image(self, level_idx):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите целую картинку", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.tab_data[level_idx]['complete_path'] = file
            self.update_tab_display(level_idx)

    def load_hole_image(self, level_idx):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите картинку с дыркой", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.tab_data[level_idx]['hole_path'] = file
            self.update_tab_display(level_idx)

    def load_patches_bulk(self, level_idx):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите заплатки (дополнят пустые места)", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return
        paths = self.tab_data[level_idx]['patches_paths']
        empty_slots = [i for i, p in enumerate(paths) if not p or not os.path.exists(p)]
        if not empty_slots:
            QMessageBox.information(self, "Информация", "Все 3 заплатки уже загружены. Удалите ненужные (ПКМ) перед загрузкой новых.")
            return
        for i, file in enumerate(files):
            if i >= len(empty_slots):
                QMessageBox.information(self, "Информация", f"Свободно только {len(empty_slots)} мест, лишние файлы не добавлены.")
                break
            paths[empty_slots[i]] = file
        self.tab_data[level_idx]['patches_paths'] = paths
        self.update_tab_display(level_idx)

    def delete_image(self, level_idx, img_type):
        if img_type == "complete":
            self.tab_data[level_idx]['complete_path'] = ""
        elif img_type == "hole":
            self.tab_data[level_idx]['hole_path'] = ""
        self.update_tab_display(level_idx)

    def delete_patch(self, level_idx, patch_idx):
        paths = self.tab_data[level_idx]['patches_paths']
        if patch_idx < len(paths):
            paths[patch_idx] = ""
            self.tab_data[level_idx]['patches_paths'] = paths
            if self.tab_data[level_idx]['correct_patch_idx'] == patch_idx:
                self.tab_data[level_idx]['correct_patch_idx'] = None
            self.update_tab_display(level_idx)

    def set_correct_patch(self, level_idx, patch_idx):
        self.tab_data[level_idx]['correct_patch_idx'] = patch_idx
        self.update_tab_display(level_idx)

    def update_tab_display(self, level_idx):
        data = self.tab_data[level_idx]
        if data['complete_path'] and os.path.exists(data['complete_path']):
            pixmap = QPixmap(data['complete_path'])
            if not pixmap.isNull():
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                data['complete_preview'].setPixmap(scaled)
            else:
                data['complete_preview'].setText("Ошибка")
        else:
            data['complete_preview'].setText("Нет")
        if data['hole_path'] and os.path.exists(data['hole_path']):
            pixmap = QPixmap(data['hole_path'])
            if not pixmap.isNull():
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                data['hole_preview'].setPixmap(scaled)
            else:
                data['hole_preview'].setText("Ошибка")
        else:
            data['hole_preview'].setText("Нет")
        for j, preview in enumerate(data['patch_previews']):
            path = data['patches_paths'][j] if j < len(data['patches_paths']) else ""
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    preview.setPixmap(scaled)
                    preview.setToolTip(os.path.basename(path))
                else:
                    preview.setText("Ошибка")
            else:
                preview.setText("Нет")
            if data['correct_patch_idx'] == j:
                preview.setStyleSheet("border: 3px solid green; border-radius: 5px; background-color: #E8F5E9;")
            else:
                preview.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
        if data['correct_patch_idx'] is not None:
            data['correct_info'].setText(f"✅ Правильная заплатка: {data['correct_patch_idx']+1}")
        else:
            data['correct_info'].setText("❌ Правильная заплатка не выбрана (кликните ЛКМ по нужной)")

    def accept(self):
        for i, data in enumerate(self.tab_data):
            if data['correct_patch_idx'] is None:
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} не выбрана правильная заплатка.")
                return
            if not data['complete_path'] or not os.path.exists(data['complete_path']):
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} не загружена целая картинка.")
                return
            if not data['hole_path'] or not os.path.exists(data['hole_path']):
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} не загружена картинка с дыркой.")
                return
            if any(not p or not os.path.exists(p) for p in data['patches_paths']):
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} не загружены все 3 заплатки.")
                return
            self.levels_data[i] = {
                "complete_image": data['complete_path'],
                "hole_image": data['hole_path'],
                "patches": data['patches_paths'],
                "correct_patch_idx": data['correct_patch_idx']
            }
        super().accept()
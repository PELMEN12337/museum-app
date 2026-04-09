import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QTabWidget, QMessageBox,
                             QWidget, QScrollArea, QGridLayout, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

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
            QDialog { background-color: #F5F5F5; }
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 8px; background-color: white; }
            QTabBar::tab { background-color: #E0E0E0; border-radius: 6px; padding: 6px 12px; margin: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #FFB74D; color: white; }
            QPushButton { background-color: #FFB74D; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; color: #5D3A1A; }
            QPushButton:hover { background-color: #FFA726; }
            QScrollArea { border: none; background-color: transparent; }
            QLabel { font-size: 13px; }
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
        self.add_level_btn.clicked.connect(self.add_level)
        self.remove_level_btn = QPushButton("➖ Удалить последний уровень")
        self.remove_level_btn.clicked.connect(self.remove_level)
        levels_btn_layout.addStretch()
        levels_btn_layout.addWidget(self.add_level_btn)
        levels_btn_layout.addWidget(self.remove_level_btn)
        levels_btn_layout.addStretch()
        main_layout.addLayout(levels_btn_layout)

        self.level_tabs = QTabWidget()
        main_layout.addWidget(self.level_tabs, 1)

        self.tab_widgets = []

        if not self.level_data:
            self._show_empty_message()
        else:
            self.rebuild_tabs()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("💾 Сохранить уровни")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def _show_empty_message(self):
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        label = QLabel("Нет уровней. Нажмите «Добавить уровень»")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")
        empty_layout.addWidget(label)
        self.level_tabs.addTab(empty_widget, "Нет уровней")

    def add_level(self):
        if self.level_tabs.count() == 1 and self.level_tabs.tabText(0) == "Нет уровней":
            self.level_tabs.clear()
            self.level_data.clear()
            self.correct_answers.clear()
        self.level_data.append([])
        self.correct_answers.append(0)
        self.rebuild_tabs()
        self.level_tabs.setCurrentIndex(len(self.level_data)-1)

    def remove_level(self):
        if len(self.level_data) == 0:
            return
        if len(self.level_data) == 1:
            self.level_data.pop()
            self.correct_answers.pop()
            self.level_tabs.clear()
            self._show_empty_message()
            return
        self.level_data.pop()
        self.correct_answers.pop()
        self.rebuild_tabs()

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
        # Проверка: для каждого уровня с изображениями должен быть выбран правильный ответ
        for i, ans in enumerate(self.correct_answers):
            if self.level_data[i] and (ans is None or ans < 0 or ans >= len(self.level_data[i])):
                QMessageBox.warning(self, "Ошибка",
                                    f"Для уровня {i+1} выберите правильный ответ (кликните на изображение).")
                return
        super().accept()
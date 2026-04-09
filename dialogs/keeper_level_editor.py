import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFileDialog, QTabWidget, QMessageBox, QWidget, QGroupBox,
                             QGridLayout, QScrollArea, QSpinBox, QLineEdit, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

class KeeperLevelEditorDialog(QDialog):
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
            QScrollArea { border: none; background-color: transparent; }
            QLabel { font-size: 13px; }
        """)

        layout = QVBoxLayout(self)
        main_layout = QVBoxLayout()
        layout.addLayout(main_layout)

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
        main_layout.addWidget(self.level_tabs)

        self.tab_data = []

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
        if self.level_tabs.count() == 1 and self.level_tabs.tabText(0) == "Нет уровней":
            self.level_tabs.clear()

        level_tab = QWidget()
        level_tab_layout = QVBoxLayout(level_tab)

        collections_control = QHBoxLayout()
        collections_control.addWidget(QLabel("Количество коллекций:"))
        spin = QSpinBox()
        spin.setRange(2, 3)   # изменено: от 2 до 3
        spin.setValue(len(level_info.get("collections", [2])))  # по умолчанию 2, если нет данных
        spin.valueChanged.connect(lambda val, idx=level_idx: self.change_collections_count(idx, val))
        collections_control.addWidget(spin)
        collections_control.addStretch()
        level_tab_layout.addLayout(collections_control)

        collections_tabs = QTabWidget()
        level_tab_layout.addWidget(collections_tabs)

        self.tab_data.append({
            'level_idx': level_idx,
            'spin': spin,
            'collections_tabs': collections_tabs,
            'collections_data': level_info.get("collections", [])
        })
        self._rebuild_level_ui(level_idx)

        self.level_tabs.addTab(level_tab, f"Уровень {level_idx+1}")

    def _rebuild_level_ui(self, level_idx):
        data = self.tab_data[level_idx]
        tabs = data['collections_tabs']
        tabs.clear()
        for col_idx, col in enumerate(data['collections_data']):
            col_tab = QWidget()
            col_layout = QVBoxLayout(col_tab)

            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Название:"))
            name_edit = QLineEdit(col.get("name", f"Коллекция {col_idx+1}"))
            name_edit.textChanged.connect(lambda text, idx=level_idx, pos=col_idx: self.set_collection_name(idx, pos, text))
            name_layout.addWidget(name_edit)
            col_layout.addLayout(name_layout)

            add_btn = QPushButton("📂 Добавить изображения")
            add_btn.clicked.connect(lambda checked, idx=level_idx, pos=col_idx: self.add_images(idx, pos))
            col_layout.addWidget(add_btn)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            container = QWidget()
            grid_layout = QGridLayout(container)
            grid_layout.setSpacing(15)
            scroll.setWidget(container)
            col_layout.addWidget(scroll)

            tabs.addTab(col_tab, col.get("name", f"Коллекция {col_idx+1}"))

            col['grid_layout'] = grid_layout
            col['images_list'] = []
            col['container'] = container

            for img_path in col.get("images", []):
                if img_path and os.path.exists(img_path):
                    self._display_image(level_idx, col_idx, img_path)
            col['images'] = [img for img in col.get('images', []) if img and os.path.exists(img)]

        QApplication.processEvents()

    def add_level(self):
        if self.level_tabs.count() == 1 and self.level_tabs.tabText(0) == "Нет уровней":
            self.level_tabs.clear()
            self.tab_data.clear()
            self.levels_data.clear()

        # Создаём уровень с 2 коллекциями по умолчанию (каждая пустая)
        new_level = {"collections": [{"name": "Коллекция 1", "images": []}, {"name": "Коллекция 2", "images": []}]}
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

    def change_collections_count(self, level_idx, new_count):
        data = self.tab_data[level_idx]
        old_count = len(data['collections_data'])
        if new_count > old_count:
            for i in range(old_count, new_count):
                data['collections_data'].append({"name": f"Коллекция {i+1}", "images": []})
        else:
            data['collections_data'] = data['collections_data'][:new_count]
        self._rebuild_level_ui(level_idx)

    def _display_image(self, level_idx, col_idx, file_path):
        data = self.tab_data[level_idx]
        col = data['collections_data'][col_idx]
        grid = col['grid_layout']
        images_list = col['images_list']
        row = len(images_list) // 3
        col_pos = len(images_list) % 3

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

        images_list.append((container, label, file_path))
        grid.addWidget(container, row, col_pos)

        label.setContextMenuPolicy(Qt.CustomContextMenu)
        label.customContextMenuRequested.connect(lambda pos, idx=level_idx, col=col_idx, img_idx=len(images_list)-1: self.delete_image(idx, col, img_idx))

    def add_images(self, level_idx, col_idx):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите изображения (максимум 9)", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return
        data = self.tab_data[level_idx]
        col = data['collections_data'][col_idx]
        current_count = len(col['images'])
        max_images = 9
        if current_count + len(files) > max_images:
            QMessageBox.warning(self, "Ошибка", f"Можно загрузить не более {max_images} изображений в коллекцию. Сейчас {current_count}, попытка добавить {len(files)}.")
            files = files[:max_images - current_count]
        for file in files:
            self._add_image_to_collection(level_idx, col_idx, file)
            QApplication.processEvents()

    def _add_image_to_collection(self, level_idx, col_idx, file_path):
        data = self.tab_data[level_idx]
        col = data['collections_data'][col_idx]
        # Проверка лимита
        if len(col['images']) >= 9:
            return
        grid = col['grid_layout']
        images_list = col['images_list']
        row = len(images_list) // 3
        col_pos = len(images_list) % 3

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

        images_list.append((container, label, file_path))
        grid.addWidget(container, row, col_pos)

        label.setContextMenuPolicy(Qt.CustomContextMenu)
        label.customContextMenuRequested.connect(lambda pos, idx=level_idx, col=col_idx, img_idx=len(images_list)-1: self.delete_image(idx, col, img_idx))

        col['images'].append(file_path)

    def delete_image(self, level_idx, col_idx, img_idx):
        reply = QMessageBox.question(self, "Удаление", "Удалить изображение?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            data = self.tab_data[level_idx]
            col = data['collections_data'][col_idx]
            images_list = col['images_list']
            if img_idx < len(images_list):
                container, _, _ = images_list[img_idx]
                grid = col['grid_layout']
                grid.removeWidget(container)
                container.deleteLater()
                del images_list[img_idx]
                del col['images'][img_idx]
                self._rebuild_grid(level_idx, col_idx)

    def _rebuild_grid(self, level_idx, col_idx):
        data = self.tab_data[level_idx]
        col = data['collections_data'][col_idx]
        grid = col['grid_layout']
        for i in reversed(range(grid.count())):
            w = grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        for idx, (container, _, _) in enumerate(col['images_list']):
            row = idx // 3
            col_pos = idx % 3
            grid.addWidget(container, row, col_pos)

    def set_collection_name(self, level_idx, col_idx, name):
        data = self.tab_data[level_idx]
        data['collections_data'][col_idx]['name'] = name
        tabs = data['collections_tabs']
        if col_idx < tabs.count():
            tabs.setTabText(col_idx, name)

    def accept(self):
        self.levels_data.clear()
        for data in self.tab_data:
            collections = []
            # Проверка количества коллекций
            if len(data['collections_data']) < 2 or len(data['collections_data']) > 3:
                QMessageBox.warning(self, "Ошибка", f"Для уровня {data['level_idx']+1} количество коллекций должно быть от 2 до 3 (сейчас {len(data['collections_data'])}).")
                return
            for col in data['collections_data']:
                # Проверка количества изображений
                img_count = len(col.get('images', []))
                if img_count < 1 or img_count > 9:
                    QMessageBox.warning(self, "Ошибка", f"Для коллекции '{col.get('name', '')}' (уровень {data['level_idx']+1}) количество изображений должно быть от 1 до 9 (сейчас {img_count}).")
                    return
                if col.get('images'):
                    collections.append({
                        "name": col.get('name', "Коллекция"),
                        "images": col['images']
                    })
            if len(collections) < 2:
                QMessageBox.warning(self, "Ошибка", f"Для уровня {data['level_idx']+1} недостаточно коллекций с изображениями.")
                return
            self.levels_data.append({"collections": collections})
        super().accept()
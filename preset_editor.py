import os
import copy
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QTabWidget, QMessageBox,
                             QWidget, QScrollArea, QGridLayout, QApplication, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from constants import ALL_HALLS, HALLS
from dialogs import (
    HallLevelEditorDialog,
    MasterLevelEditorDialog,
    RestorerLevelEditorDialog,
    KeeperLevelEditorDialog
)

class PresetEditor(QDialog):
    def __init__(self, preset_manager, parent=None, preset_data=None, preset_index=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.preset_index = preset_index
        self.setWindowTitle("Редактор пресета" if preset_index is not None else "Создание пресета")
        self.setMinimumSize(900, 700)
        self.resize(1230, 820)
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; }
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 8px; background-color: white; }
            QTabBar::tab { background-color: #E0E0E0; border-radius: 6px; padding: 6px 12px; margin: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #FFB74D; color: white; }
            QPushButton { background-color: #FFB74D; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; color: #5D3A1A; }
            QPushButton:hover { background-color: #FFA726; }
            QLineEdit { border: 1px solid #CCC; border-radius: 6px; padding: 6px; }
            QLabel { color: #333; }
            QComboBox { border: 1px solid #CCC; border-radius: 6px; padding: 4px; background-color: white; }
            QScrollArea { border: none; background-color: transparent; }
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
        self.main_tabs.setTabPosition(QTabWidget.North)
        self.main_tabs.setStyleSheet("""
            QTabBar::tab {
                font-size: 11px;
                padding: 6px 8px;
                margin: 2px;
                min-width: 200px;
            }
        """)
        main_layout.addWidget(self.main_tabs, 1)

        self.tab_data = {}

        for hall_name in ALL_HALLS:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            setup_btn = QPushButton(f"Настроить уровни для зала «{hall_name}»")
            setup_btn.clicked.connect(lambda checked, name=hall_name: self.setup_hall_levels(name))
            tab_layout.addWidget(setup_btn)

            level_combo = QComboBox()
            tab_layout.addWidget(level_combo)

            preview_scroll = QScrollArea()
            preview_scroll.setWidgetResizable(True)
            preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            tab_layout.addWidget(preview_scroll)

            self.tab_data[hall_name] = {
                "level_data": None,
                "correct_answers": None,
                "level_combo": level_combo,
                "preview_scroll": preview_scroll,
                "preview_widget": None,
            }

            def make_update_preview(hall):
                def update_preview(level_index):
                    new_widget = QWidget()
                    new_layout = QVBoxLayout(new_widget)
                    new_layout.setSpacing(10)
                    new_layout.setContentsMargins(5, 5, 5, 5)

                    level_data = self.tab_data[hall]["level_data"]
                    if level_data and level_index < len(level_data):
                        scroll = self.tab_data[hall]["preview_scroll"]
                        scroll.updateGeometry()
                        QApplication.processEvents()
                        available_width = scroll.width() - 20
                        if available_width < 100:
                            parent_w = scroll.parentWidget().width() if scroll.parentWidget() else 0
                            if parent_w > 100:
                                available_width = parent_w - 20
                            else:
                                available_width = 400

                        if hall == "Зал мастера (Подбери цвета по картинке)":
                            level_dict = level_data[level_index]
                            new_layout.addSpacing(10)
                            fixed_height = 230
                            main_path = level_dict.get("main_image", "")
                            if main_path and os.path.exists(main_path):
                                main_label = QLabel()
                                pixmap = QPixmap(main_path)
                                if not pixmap.isNull():
                                    scaled = pixmap.scaledToHeight(fixed_height, Qt.SmoothTransformation)
                                    max_width = available_width // 2
                                    if scaled.width() > max_width:
                                        scaled = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
                                    main_label.setPixmap(scaled)
                                    main_label.setFixedSize(scaled.width(), scaled.height())
                                    main_label.setAlignment(Qt.AlignCenter)
                                    main_label.setStyleSheet("border: 2px solid #FFB74D; border-radius: 5px; background: white;")
                                    new_layout.addWidget(main_label, alignment=Qt.AlignCenter)
                                    new_layout.addSpacing(15)
                            color_paths = level_dict.get("color_images", [])
                            if color_paths:
                                colors_layout = QGridLayout()
                                colors_layout.setSpacing(15)
                                spacing = colors_layout.spacing()
                                cell_width = (available_width - spacing * 3) // 4
                                cell_width = max(60, min(cell_width, 90))
                                for idx, img_path in enumerate(color_paths):
                                    if img_path and os.path.exists(img_path):
                                        label = QLabel()
                                        pixmap = QPixmap(img_path)
                                        if not pixmap.isNull():
                                            w = pixmap.width()
                                            h = pixmap.height()
                                            side = min(w, h)
                                            x = (w - side) // 2
                                            y = (h - side) // 2
                                            square = pixmap.copy(x, y, side, side)
                                            scaled = square.scaled(cell_width, cell_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                            label.setPixmap(scaled)
                                            label.setFixedSize(cell_width, cell_width)
                                            label.setAlignment(Qt.AlignCenter)
                                            label.setStyleSheet("border: 1px solid gray; border-radius: 5px; background: white;")
                                            colors_layout.addWidget(label, idx // 4, idx % 4)
                                new_layout.addLayout(colors_layout)
                                new_layout.addStretch()
                        elif hall == "Зал реставратора (Заплатки)":
                            level_dict = level_data[level_index]
                            new_layout.addSpacing(10)
                            hole_path = level_dict.get("hole_image", "")
                            if hole_path and os.path.exists(hole_path):
                                hole_label = QLabel()
                                pixmap = QPixmap(hole_path)
                                if not pixmap.isNull():
                                    max_height = 300
                                    scaled = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
                                    hole_label.setPixmap(scaled)
                                    hole_label.setFixedSize(scaled.width(), scaled.height())
                                    hole_label.setAlignment(Qt.AlignCenter)
                                    hole_label.setStyleSheet("border: 2px solid #FFB74D; border-radius: 5px; background: white;")
                                    new_layout.addWidget(hole_label, alignment=Qt.AlignCenter)
                                    new_layout.addSpacing(20)
                            patches = level_dict.get("patches", [])
                            if patches and any(p for p in patches):
                                patches_layout = QHBoxLayout()
                                patches_layout.setSpacing(20)
                                for idx, patch_path in enumerate(patches):
                                    if patch_path and os.path.exists(patch_path):
                                        label = QLabel()
                                        pixmap = QPixmap(patch_path)
                                        if not pixmap.isNull():
                                            cell_size = min(available_width // 5, 120)
                                            scaled = pixmap.scaled(cell_size, cell_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                            label.setPixmap(scaled)
                                            label.setFixedSize(cell_size, cell_size)
                                            label.setAlignment(Qt.AlignCenter)
                                            label.setStyleSheet("border: 1px solid gray; border-radius: 5px; background: white;")
                                            patches_layout.addWidget(label)
                                new_layout.addLayout(patches_layout)
                                new_layout.addStretch()
                        elif hall == "Зал хранителя (Сортировка по коллекциям)":
                            level_dict = level_data[level_index]
                            collections = level_dict.get("collections", [])
                            if collections:
                                for col in collections:
                                    col_name = col.get("name", "Без названия")
                                    col_label = QLabel(col_name)
                                    col_label.setStyleSheet("font-weight: bold;")
                                    new_layout.addWidget(col_label)
                                    images = col.get("images", [])
                                    if images:
                                        img_layout = QHBoxLayout()
                                        for idx, img_path in enumerate(images[:3]):
                                            if img_path and os.path.exists(img_path):
                                                pixmap = QPixmap(img_path)
                                                if not pixmap.isNull():
                                                    label = QLabel()
                                                    scaled = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                                    label.setPixmap(scaled)
                                                    label.setFixedSize(60, 60)
                                                    img_layout.addWidget(label)
                                        new_layout.addLayout(img_layout)
                        else:
                            # Обычные залы
                            img_list = level_data[level_index]
                            if img_list:
                                images_layout = QGridLayout()
                                images_layout.setSpacing(10)
                                spacing = images_layout.spacing()
                                cell_width = (available_width - spacing * 2) // 3
                                cell_width = max(80, min(cell_width, 400))
                                for idx, img_path in enumerate(img_list):
                                    if img_path and os.path.exists(img_path):
                                        label = QLabel()
                                        pixmap = QPixmap(img_path)
                                        if not pixmap.isNull():
                                            scaled = pixmap.scaled(cell_width, cell_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                            label.setPixmap(scaled)
                                            label.setFixedSize(cell_width, cell_width)
                                            label.setAlignment(Qt.AlignCenter)
                                            label.setStyleSheet("border: 1px solid gray; border-radius: 5px; background: white;")
                                            images_layout.addWidget(label, idx // 3, idx % 3)
                                new_layout.addLayout(images_layout)
                    else:
                        label = QLabel("Нет изображений")
                        label.setAlignment(Qt.AlignCenter)
                        new_layout.addWidget(label)

                    scroll = self.tab_data[hall]["preview_scroll"]
                    old = self.tab_data[hall].get("preview_widget")
                    if old:
                        old.setParent(None)
                    scroll.setWidget(new_widget)
                    self.tab_data[hall]["preview_widget"] = new_widget

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
        QTimer.singleShot(100, self.update_all_previews)

    def _update_preview_combo(self, hall_name):
        data = self.tab_data[hall_name]
        combo = data["level_combo"]
        combo.clear()
        if data["level_data"] is not None:
            for i in range(len(data["level_data"])):
                combo.addItem(f"Уровень {i+1}")
            combo.setCurrentIndex(0)
        else:
            combo.addItem("Нет уровней")

    def setup_hall_levels(self, hall_name):
        data = self.tab_data[hall_name]
        if hall_name == "Зал мастера (Подбери цвета по картинке)":
            if data["level_data"] is None:
                data["level_data"] = []
                data["correct_answers"] = []
            level_data_copy = copy.deepcopy(data["level_data"])
            editor = MasterLevelEditorDialog(hall_name, level_data_copy, self)
            if editor.exec_():
                data["level_data"] = level_data_copy
                self._update_preview_combo(hall_name)
        elif hall_name == "Зал реставратора (Заплатки)":
            if data["level_data"] is None:
                data["level_data"] = []
                data["correct_answers"] = []
            level_data_copy = copy.deepcopy(data["level_data"])
            editor = RestorerLevelEditorDialog(hall_name, level_data_copy, self)
            if editor.exec_():
                data["level_data"] = level_data_copy
                self._update_preview_combo(hall_name)
        elif hall_name == "Зал хранителя (Сортировка по коллекциям)":
            if data["level_data"] is None:
                data["level_data"] = []
                data["correct_answers"] = []
            level_data_copy = copy.deepcopy(data["level_data"])
            editor = KeeperLevelEditorDialog(hall_name, level_data_copy, self)
            if editor.exec_():
                data["level_data"] = level_data_copy
                self._update_preview_combo(hall_name)
        else:
            # Обычные залы (внимание, знакомство)
            if data["level_data"] is None:
                data["level_data"] = []
                data["correct_answers"] = []
            # Прямая передача ссылок
            editor = HallLevelEditorDialog(hall_name, data["level_data"], data["correct_answers"], self)
            if editor.exec_():
                # Данные уже обновлены
                self._update_preview_combo(hall_name)

    def accept(self):
        # ОТЛАДКА: убедимся, что метод вызывается
        print("\n=== PresetEditor.accept CALLED ===")
        if not self.preset_name.text().strip():
            print("ERROR: preset name is empty")
            QMessageBox.warning(self, "Ошибка", "Введите название пресета.")
            return

        any_configured = False
        for hall_name, data in self.tab_data.items():
            if data["level_data"] is not None:
                any_configured = True
                if hall_name == "Зал мастера (Подбери цвета по картинке)":
                    for i, level_dict in enumerate(data["level_data"]):
                        if not level_dict.get("main_image"):
                            QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит основной картинки.")
                            return
                        if len(level_dict.get("color_images", [])) != 8 or any(not c for c in level_dict["color_images"]):
                            QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит 8 цветов.")
                            return
                elif hall_name == "Зал реставратора (Заплатки)":
                    for i, level_dict in enumerate(data["level_data"]):
                        if not level_dict.get("complete_image"):
                            QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит целой картинки.")
                            return
                        if not level_dict.get("hole_image"):
                            QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит картинки с дыркой.")
                            return
                        if len(level_dict.get("patches", [])) != 3 or any(not p for p in level_dict["patches"]):
                            QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит 3 заплаток.")
                            return
                elif hall_name == "Зал хранителя (Сортировка по коллекциям)":
                    # Проверка, что в каждом уровне есть коллекции с изображениями
                    for i, level_dict in enumerate(data["level_data"]):
                        if not level_dict.get("collections"):
                            QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} не содержит коллекций.")
                            return
                        for col in level_dict["collections"]:
                            if not col.get("images"):
                                QMessageBox.warning(self, "Ошибка", f"Для зала «{hall_name}» уровень {i+1} коллекция '{col.get('name')}' не содержит изображений.")
                                return
                else:
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

        # Копируем изображения
        for hall_name, hall_data in halls_data.items():
            if hall_name == "Зал мастера (Подбери цвета по картинке)":
                for level_idx, level_dict in enumerate(hall_data["levels"]):
                    new_level = self.preset_manager.copy_master_images_to_preset(
                        preset["name"], hall_name, level_idx+1, level_dict
                    )
                    hall_data["levels"][level_idx] = new_level
            elif hall_name == "Зал реставратора (Заплатки)":
                for level_idx, level_dict in enumerate(hall_data["levels"]):
                    new_level = self.preset_manager.copy_restorer_images_to_preset(
                        preset["name"], hall_name, level_idx+1, level_dict
                    )
                    hall_data["levels"][level_idx] = new_level
            elif hall_name == "Зал хранителя (Сортировка по коллекциям)":
                for level_idx, level_dict in enumerate(hall_data["levels"]):
                    new_level = self.preset_manager.copy_keeper_images_to_preset(
                        preset["name"], hall_name, level_idx+1, level_dict
                    )
                    hall_data["levels"][level_idx] = new_level
            else:
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

        print("Preset saved successfully!")
        super().accept()

    def resizeEvent(self, event):
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, self._delayed_resize)
        super().resizeEvent(event)

    def _delayed_resize(self):
        for hall_name, data in self.tab_data.items():
            combo = data.get("level_combo")
            if combo and combo.count() > 0:
                current_index = combo.currentIndex()
                if current_index >= 0:
                    combo.setCurrentIndex(current_index)

    def showEvent(self, event):
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QApplication
        QTimer.singleShot(500, self.update_all_previews)
        QApplication.processEvents()
        super().showEvent(event)

    def update_all_previews(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        for hall_name, data in self.tab_data.items():
            combo = data.get("level_combo")
            if combo and combo.count() > 0:
                current_index = combo.currentIndex()
                if current_index >= 0:
                    scroll = data.get("preview_scroll")
                    if scroll:
                        scroll.updateGeometry()
                        QApplication.processEvents()
                    combo.setCurrentIndex(current_index)
import os
import copy
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QTabWidget, QMessageBox,
                             QWidget, QScrollArea, QGridLayout, QApplication, QComboBox,
                             QCheckBox, QMenu, QAction, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QCursor
from constants import ALL_HALLS, HALLS

# ----------------------------------------------------------------------
# Диалог для обычных залов (внимание, знакомство, реставратор, хранитель)
# ----------------------------------------------------------------------
class HallLevelEditorDialog(QDialog):
    def __init__(self, hall_name, total_levels, level_data, correct_answers, parent=None):
        super().__init__(parent)
        self.hall_name = hall_name
        self.total_levels = total_levels
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
            QPushButton:pressed { background-color: #F57C00; }
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

        # Кнопки добавления/удаления уровней (для обычных залов)
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
        self.setStyleSheet("""
            QDialog { background-color: #F5F5F5; }
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 8px; background-color: white; }
            QTabBar::tab { background-color: #E0E0E0; border-radius: 6px; padding: 6px 12px; margin: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #FFB74D; color: white; }
            QPushButton { background-color: #FFB74D; border: none; border-radius: 8px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #FFA726; }
        """)

        layout = QVBoxLayout(self)
        self.level_tabs = QTabWidget()
        layout.addWidget(self.level_tabs)

        self.tab_data = []

        for i, level_info in enumerate(self.levels_data):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            # Основная картинка
            tab_layout.addWidget(QLabel("Основная картинка (узор):"))
            main_btn = QPushButton("Загрузить основную картинку")
            main_btn.clicked.connect(lambda checked, idx=i: self.load_main_image(idx))
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
            load_colors_btn.clicked.connect(lambda checked, idx=i: self.add_color_images(idx))
            tab_layout.addWidget(load_colors_btn)

            # Счетчик загруженных цветов
            colors_counter = QLabel("Загружено цветов: 0 / 8")
            colors_counter.setStyleSheet("color: red; font-weight: bold;")
            tab_layout.addWidget(colors_counter)

            # Сетка для миниатюр цветов
            colors_grid = QGridLayout()
            color_labels = []
            color_widgets = []  # для хранения контейнеров
            for j in range(8):
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                label = QLabel()
                label.setFixedSize(100, 100)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
                label.mousePressEvent = lambda event, idx=i, pos=j: self.on_color_click(event, idx, pos)
                name_label = QLabel(f"Цвет {j+1}")
                name_label.setAlignment(Qt.AlignCenter)
                container_layout.addWidget(label)
                container_layout.addWidget(name_label)
                colors_grid.addWidget(container, j//4, j%4)
                color_labels.append(label)
                color_widgets.append(container)
            tab_layout.addLayout(colors_grid)

            self.level_tabs.addTab(tab, f"Уровень {i+1}")
            self.tab_data.append({
                'level_idx': i,
                'main_preview': main_preview,
                'color_labels': color_labels,
                'color_widgets': color_widgets,
                'colors_counter': colors_counter,
                'main_path': level_info.get("main_image", ""),
                'color_paths': level_info.get("color_images", [""]*8),
                'correct_indices': set(level_info.get("correct_indices", []))
            })
            self.update_tab_display(i)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Сохранить уровни")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_main_image(self, level_idx):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите основную картинку", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.tab_data[level_idx]['main_path'] = file
            self.update_tab_display(level_idx)

    def add_color_images(self, level_idx):
        data = self.tab_data[level_idx]
        current_paths = data['color_paths'][:]
        # Находим пустые позиции
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
        """Удаляет изображение цвета по указанной позиции (очищает путь)."""
        data = self.tab_data[level_idx]
        if data['color_paths'][pos] and os.path.exists(data['color_paths'][pos]):
            data['color_paths'][pos] = ""
            # Также удаляем этот цвет из правильных, если он там был
            if pos in data['correct_indices']:
                data['correct_indices'].remove(pos)
            self.update_tab_display(level_idx)
        else:
            QMessageBox.information(self, "Удаление", "В этой позиции нет изображения.")

    def update_tab_display(self, level_idx):
        data = self.tab_data[level_idx]
        # Основная картинка
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

        # Цвета
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
            # Увеличенная обводка для правильных цветов
            if j in data['correct_indices']:
                label.setStyleSheet("border: 4px solid green; border-radius: 5px; background-color: #E8F5E9;")
            else:
                label.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")

    def accept(self):
        # Проверяем, что для каждого уровня загружены все 8 цветов и основная картинка
        for i, data in enumerate(self.tab_data):
            color_paths = data['color_paths']
            loaded_count = sum(1 for p in color_paths if p and os.path.exists(p))
            if loaded_count != 8:
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} загружено {loaded_count} цветов, нужно 8.")
                return
            if not data['main_path'] or not os.path.exists(data['main_path']):
                QMessageBox.warning(self, "Ошибка", f"Для уровня {i+1} не загружена основная картинка.")
                return
        # Сохраняем
        for i, data in enumerate(self.tab_data):
            self.levels_data[i] = {
                "main_image": data['main_path'],
                "color_images": data['color_paths'],
                "correct_indices": list(data['correct_indices'])
            }
        super().accept()

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
        self.level_tabs = QTabWidget()
        layout.addWidget(self.level_tabs)

        self.tab_data = []
        for i, level_info in enumerate(self.levels_data):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setSpacing(15)

            # Целая картинка
            complete_group = QGroupBox("Целая картинка (без дефекта)")
            complete_layout = QVBoxLayout(complete_group)
            complete_btn = QPushButton("📂 Загрузить целую картинку")
            complete_btn.clicked.connect(lambda checked, idx=i: self.load_complete_image(idx))
            complete_layout.addWidget(complete_btn)
            complete_preview = QLabel()
            complete_preview.setFixedSize(200, 200)
            complete_preview.setAlignment(Qt.AlignCenter)
            complete_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
            complete_preview.setContextMenuPolicy(Qt.CustomContextMenu)
            complete_preview.customContextMenuRequested.connect(lambda pos, idx=i: self.delete_image(idx, "complete"))
            complete_layout.addWidget(complete_preview, alignment=Qt.AlignCenter)
            tab_layout.addWidget(complete_group)

            # Картинка с дыркой
            hole_group = QGroupBox("Картинка с дыркой")
            hole_layout = QVBoxLayout(hole_group)
            hole_btn = QPushButton("📂 Загрузить картинку с дыркой")
            hole_btn.clicked.connect(lambda checked, idx=i: self.load_hole_image(idx))
            hole_layout.addWidget(hole_btn)
            hole_preview = QLabel()
            hole_preview.setFixedSize(200, 200)
            hole_preview.setAlignment(Qt.AlignCenter)
            hole_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
            hole_preview.setContextMenuPolicy(Qt.CustomContextMenu)
            hole_preview.customContextMenuRequested.connect(lambda pos, idx=i: self.delete_image(idx, "hole"))
            hole_layout.addWidget(hole_preview, alignment=Qt.AlignCenter)
            tab_layout.addWidget(hole_group)

            # Заплатки (3 штуки)
            patches_group = QGroupBox("Заплатки (3 изображения) – клик ЛКМ – выбрать правильную, ПКМ – удалить")
            patches_layout = QVBoxLayout(patches_group)
            patches_btn = QPushButton("📂 Загрузить заплатки (дополнят пустые места)")
            patches_btn.clicked.connect(lambda checked, idx=i: self.load_patches_bulk(idx))
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
                label.customContextMenuRequested.connect(lambda pos, idx=i, pos_idx=j: self.delete_patch(idx, pos_idx))
                label.mousePressEvent = lambda event, idx=i, pos=j: self.set_correct_patch(idx, pos) if event.button() == Qt.LeftButton else None
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

            self.level_tabs.addTab(tab, f"Уровень {i+1}")
            self.tab_data.append({
                'level_idx': i,
                'complete_preview': complete_preview,
                'hole_preview': hole_preview,
                'patch_previews': patch_previews,
                'correct_info': correct_info,
                'complete_path': level_info.get("complete_image", ""),
                'hole_path': level_info.get("hole_image", ""),
                'patches_paths': level_info.get("patches", [""]*3),
                'correct_patch_idx': level_info.get("correct_patch_idx", None)
            })
            self.update_tab_display(i)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("💾 Сохранить уровни")
        self.cancel_btn = QPushButton("❌ Отмена")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

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
        # Находим пустые слоты
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
        # Целая картинка
        if data['complete_path'] and os.path.exists(data['complete_path']):
            pixmap = QPixmap(data['complete_path'])
            if not pixmap.isNull():
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                data['complete_preview'].setPixmap(scaled)
            else:
                data['complete_preview'].setText("Ошибка")
        else:
            data['complete_preview'].setText("Нет")
        # Дырка
        if data['hole_path'] and os.path.exists(data['hole_path']):
            pixmap = QPixmap(data['hole_path'])
            if not pixmap.isNull():
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                data['hole_preview'].setPixmap(scaled)
            else:
                data['hole_preview'].setText("Ошибка")
        else:
            data['hole_preview'].setText("Нет")
        # Заплатки
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
            # Выделяем правильную заплатку
            if data['correct_patch_idx'] == j:
                preview.setStyleSheet("border: 3px solid green; border-radius: 5px; background-color: #E8F5E9;")
            else:
                preview.setStyleSheet("border: 2px solid gray; border-radius: 5px; background-color: white;")
        # Информация о правильной заплатке
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

# ----------------------------------------------------------------------
# Главный диалог PresetEditor
# ----------------------------------------------------------------------
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

            # Функция обновления предпросмотра (упрощённо, но с адаптацией)
            def make_update_preview(hall):
                def update_preview(level_index):
                    new_widget = QWidget()
                    new_layout = QVBoxLayout(new_widget)
                    new_layout.setSpacing(10)
                    new_layout.setContentsMargins(5, 5, 5, 5)

                    level_data = self.tab_data[hall]["level_data"]
                    if level_data and level_index < len(level_data):
                        # Принудительно обновляем геометрию скролл-области
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
                                            # обрезаем до квадрата
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
                                    # Ограничение по высоте (максимум 300), ширина пропорциональна
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
                                            # Заплатки остаются квадратными, но можно тоже по высоте
                                            cell_size = min(available_width // 5, 120)
                                            scaled = pixmap.scaled(cell_size, cell_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                            label.setPixmap(scaled)
                                            label.setFixedSize(cell_size, cell_size)
                                            label.setAlignment(Qt.AlignCenter)
                                            label.setStyleSheet("border: 1px solid gray; border-radius: 5px; background: white;")
                                            patches_layout.addWidget(label)
                                new_layout.addLayout(patches_layout)
                                new_layout.addStretch()
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
                data["level_data"] = [{"main_image": "", "color_images": [""]*8, "correct_indices": []}]
                data["correct_answers"] = [0]
            level_data_copy = copy.deepcopy(data["level_data"])
            editor = MasterLevelEditorDialog(hall_name, level_data_copy, self)
            if editor.exec_():
                data["level_data"] = level_data_copy
                self._update_preview_combo(hall_name)
        elif hall_name == "Зал реставратора (Заплатки)":
            if data["level_data"] is None:
                data["level_data"] = [{"complete_image": "", "hole_image": "", "patches": [""]*3, "correct_patch_idx": 0}]
                data["correct_answers"] = [0]
            level_data_copy = copy.deepcopy(data["level_data"])
            editor = RestorerLevelEditorDialog(hall_name, level_data_copy, self)
            if editor.exec_():
                data["level_data"] = level_data_copy
                self._update_preview_combo(hall_name)
        else:
            # Обычные залы
            if data["level_data"] is None:
                default_levels = 1
                data["level_data"] = [[] for _ in range(default_levels)]
                data["correct_answers"] = [0] * default_levels
            level_data_copy = copy.deepcopy(data["level_data"])
            correct_answers_copy = copy.deepcopy(data["correct_answers"])
            editor = HallLevelEditorDialog(hall_name, len(level_data_copy), level_data_copy, correct_answers_copy, self)
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
        # Увеличенная задержка и принудительная обработка событий
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
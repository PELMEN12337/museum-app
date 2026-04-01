import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

HALLS = {
    "Зал внимания (Найди лишний)": 3,
    "Зал знакомства (Найди такую же)": 4,
    "Зал мастера (Подбери цвета по картинке)": 4,
    "Зал реставратора (Заплатки)": 4,
    "Зал хранителя (Сортировка по коллекциям)": 3
}

HALL_EMOJI = {
    "Зал внимания (Найди лишний)": "🔍",
    "Зал знакомства (Найди такую же)": "👯",
    "Зал мастера (Подбери цвета по картинке)": "🎨",
    "Зал реставратора (Заплатки)": "🧩",
    "Зал хранителя (Сортировка по коллекциям)": "🏛️"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Музейные приключения 🎨")
        self.setMinimumSize(900, 700)
        self.setFocusPolicy(Qt.StrongFocus)

        # Центральный виджет с вертикальной компоновкой
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель с кнопкой полного экрана
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: rgba(255, 200, 150, 100); border-bottom-left-radius: 20px; border-bottom-right-radius: 20px;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)

        # Пустое пространство слева, чтобы кнопка была справа
        top_layout.addStretch()

        self.fullscreen_btn = QPushButton("🖥️ Полный экран")
        self.fullscreen_btn.setFixedSize(150, 40)
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFA07A;
                border-radius: 20px;
                font-size: 14px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #FF8C69;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        top_layout.addWidget(self.fullscreen_btn)

        main_layout.addWidget(top_bar)

        # Стек для экранов
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Создаём экраны
        self.start_screen = StartScreen(self)
        self.hall_screen = HallSelectionScreen(self)

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.hall_screen)

        self.start_screen.start_clicked.connect(self.show_hall_selection)

        # Текущий экран уровня
        self.current_hall_screen = None
        self.current_hall = None
        self.current_level = None

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("🖥️ Полный экран")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("🖥️ Выход из полного экрана")
        # Обновляем размеры картинок, если на экране уровня
        if self.current_hall_screen:
            self.current_hall_screen.resize_images()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def show_hall_selection(self):
        self.stack.setCurrentWidget(self.hall_screen)

    def show_level(self, hall_name, level):
        # Если мы уже в том же зале – обновляем существующий экран
        if self.current_hall == hall_name and self.current_hall_screen is not None:
            self.current_hall_screen.set_level(hall_name, level)
            self.stack.setCurrentWidget(self.current_hall_screen)
        else:
            # Создаём новый экран для другого зала
            total_levels = HALLS[hall_name]
            level_screen = LevelScreen(hall_name, level, total_levels, self)
            self.stack.addWidget(level_screen)
            self.current_hall_screen = level_screen
            self.current_hall = hall_name
            self.stack.setCurrentWidget(level_screen)
        self.current_level = level

    def show_hall_selection_from_level(self):
        self.stack.setCurrentWidget(self.hall_screen)

    def navigate_to(self, hall_name, level):
        if hall_name in HALLS and 1 <= level <= HALLS[hall_name]:
            self.show_level(hall_name, level)

    def next_level(self, hall_name, current_level):
        total_levels = HALLS[hall_name]
        if current_level < total_levels:
            self.show_level(hall_name, current_level + 1)
        else:
            QMessageBox.information(self, "Поздравляем!",
                                    f"🎉 Вы прошли все уровни зала '{hall_name}'! 🎉\n"
                                    "Выберите другой зал или вернитесь в главное меню.")
            self.show_hall_selection_from_level()


class StartScreen(QWidget):
    start_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        title = QLabel("🏛️ Добро пожаловать в музей! 🎨")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Comic Sans MS", 32, QFont.Bold))
        title.setStyleSheet("color: #FF6F00; margin: 30px;")
        layout.addWidget(title)

        self.image_label = QLabel()
        self.image_label.setText("🎭🎨🖌️🏺🖼️")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFont(QFont("Segoe UI Emoji", 48))
        layout.addWidget(self.image_label)

        self.start_btn = QPushButton("🚀 Начать приключение! 🚀")
        self.start_btn.setFixedSize(350, 70)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB74D;
                font-size: 20px;
                border-radius: 35px;
            }
            QPushButton:hover {
                background-color: #FFA726;
            }
        """)
        self.start_btn.clicked.connect(self.on_start)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

    def on_start(self):
        self.start_clicked.emit()


class HallSelectionScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        label = QLabel("🎪 Выбери свой зал! 🎪")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Comic Sans MS", 24, QFont.Bold))
        label.setStyleSheet("color: #BF360C; margin: 20px;")
        layout.addWidget(label)

        for hall_name in HALLS.keys():
            emoji = HALL_EMOJI.get(hall_name, "🎨")
            btn = QPushButton(f"{emoji} {hall_name} {emoji}")
            btn.setFixedSize(500, 60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #66BB6A;
                    font-size: 16px;
                    border-radius: 30px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                }
            """)
            btn.clicked.connect(lambda checked, name=hall_name: self.select_hall(name))
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        back_btn = QPushButton("◀ На главную")
        back_btn.setFixedSize(200, 50)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF8A65;
                font-size: 14px;
                border-radius: 25px;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

    def select_hall(self, hall_name):
        if self.parent:
            self.parent.show_level(hall_name, 1)

    def go_back(self):
        if self.parent:
            self.parent.stack.setCurrentIndex(0)


class LevelScreen(QWidget):
    def __init__(self, hall_name, level, total_levels, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.hall_name = hall_name
        self.level = level
        self.total_levels = total_levels

        self.original_pixmaps = []
        self.is_odd = [False, False, False]

        # Загрузка картинок
        self.hall_index = list(HALLS.keys()).index(hall_name) + 1
        self.load_images()

        # Интерфейс
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)

        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 200, 150);
                border-radius: 20px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Comic Sans MS", 20, QFont.Bold))
        self.title_label.setStyleSheet("color: #5D3A1A;")

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Comic Sans MS", 14))

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.info_label)
        main_layout.addWidget(info_frame)

        self.images_layout = QHBoxLayout()
        self.image_labels = []
        for i in range(3):
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid #FFB74D; border-radius: 10px; padding: 5px;")
            label.mousePressEvent = lambda event, idx=i: self.on_image_click(idx)
            self.image_labels.append(label)
            self.images_layout.addWidget(label)

        main_layout.addLayout(self.images_layout)

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(15)

        self.nav_btn = QPushButton("🗺️ Навигация по залам и уровням 🗺️")
        self.nav_btn.setFixedHeight(50)
        self.nav_btn.clicked.connect(self.open_navigation)
        button_layout.addWidget(self.nav_btn)

        level_buttons = QHBoxLayout()
        self.prev_btn = QPushButton("◀ Предыдущий уровень")
        self.prev_btn.setFixedHeight(50)
        self.next_btn = QPushButton("Следующий уровень ▶")
        self.next_btn.setFixedHeight(50)
        self.prev_btn.clicked.connect(self.prev_level)
        self.next_btn.clicked.connect(self.next_level)
        level_buttons.addWidget(self.prev_btn)
        level_buttons.addWidget(self.next_btn)
        button_layout.addLayout(level_buttons)

        self.hall_btn = QPushButton("🏛️ Выбор другого зала 🏛️")
        self.hall_btn.setFixedHeight(50)
        self.hall_btn.clicked.connect(self.go_to_hall_selection)
        button_layout.addWidget(self.hall_btn)

        main_layout.addWidget(button_frame)

        self.update_display()
        self.resize_images()

    def load_images(self):
        """Загружает картинки для текущего уровня."""
        self.original_pixmaps.clear()
        for i in range(1, 4):
            base_filename = f"{self.hall_index}-{self.level}-{i}"
            odd_filename = f"{base_filename}(f).jpg"
            normal_filename = f"{base_filename}.jpg"

            odd_path = os.path.join(IMAGES_DIR, odd_filename)
            self.is_odd[i-1] = os.path.exists(odd_path)

            filepath = os.path.join(IMAGES_DIR, normal_filename)
            if not os.path.exists(filepath):
                filepath = os.path.join(IMAGES_DIR, odd_filename)
            if os.path.exists(filepath):
                pixmap = QPixmap(filepath)
                if pixmap.isNull():
                    pixmap = self.create_placeholder()
                self.original_pixmaps.append(pixmap)
            else:
                pixmap = self.create_placeholder()
                self.original_pixmaps.append(pixmap)

    def set_level(self, hall_name, level):
        """Обновляет уровень в текущем экране."""
        self.hall_name = hall_name
        self.level = level
        self.total_levels = HALLS[hall_name]
        self.hall_index = list(HALLS.keys()).index(hall_name) + 1
        self.load_images()
        self.update_display()
        self.resize_images()

    def create_placeholder(self):
        pixmap = QPixmap(300, 300)
        pixmap.fill(Qt.gray)
        return pixmap

    def resize_images(self):
        """Динамически изменяет размер картинок в зависимости от ширины окна."""
        if not hasattr(self, 'image_labels') or not self.image_labels:
            return
        available_width = self.width() - 100
        image_width = max(100, available_width // 3)
        for i, label in enumerate(self.image_labels):
            if i < len(self.original_pixmaps):
                pixmap = self.original_pixmaps[i]
                scaled = pixmap.scaled(image_width, image_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled)
                label.setFixedSize(scaled.width(), scaled.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_images()

    def update_display(self):
        emoji = HALL_EMOJI.get(self.hall_name, "🎨")
        self.title_label.setText(f"{emoji} {self.hall_name} {emoji}")
        self.info_label.setText(f"Уровень {self.level} из {self.total_levels}")
        self.prev_btn.setEnabled(self.level > 1)
        self.next_btn.setEnabled(self.level < self.total_levels)

    def on_image_click(self, index):
        if self.is_odd[index]:
            QMessageBox.information(self, "Правильно!",
                                    "🎉 Молодец! Это лишняя картинка! 🎉")
            if self.parent:
                self.parent.next_level(self.hall_name, self.level)
        else:
            QMessageBox.warning(self, "Неправильно",
                                "❌ Это не лишняя картинка. Попробуй ещё раз! ❌")

    def prev_level(self):
        if self.level > 1:
            if self.parent:
                self.parent.show_level(self.hall_name, self.level - 1)

    def next_level(self):
        if self.level < self.total_levels:
            if self.parent:
                self.parent.show_level(self.hall_name, self.level + 1)

    def go_to_hall_selection(self):
        if self.parent:
            self.parent.show_hall_selection_from_level()

    def open_navigation(self):
        from navigation_dialog import NavigationDialog
        dialog = NavigationDialog(self.parent, self.hall_name, self.level)
        if dialog.exec_():
            hall, level = dialog.get_selection()
            if hall and level:
                self.parent.navigate_to(hall, level)
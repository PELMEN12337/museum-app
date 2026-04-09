from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, \
    QGridLayout, QApplication, QSizePolicy, QMessageBox, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from halls import (
    AttentionHallLevel, FamiliarityHallLevel, MasterHallLevel,
    RestorerHallLevel, KeeperHallLevel
)
from themes import THEMES
from preset_manager import PresetManager
from constants import HALLS
from preset_manager_dialog import PresetManagerDialog
from version import VERSION

HALL_CLASSES = {
    "Зал внимания (Найди лишний)": AttentionHallLevel,
    "Зал знакомства (Найди такую же)": FamiliarityHallLevel,
    "Зал мастера (Подбери цвета по картинке)": MasterHallLevel,
    "Зал реставратора (Заплатки)": RestorerHallLevel,
    "Зал хранителя (Сортировка по коллекциям)": KeeperHallLevel,
}

class MainWindow(QMainWindow):
    fullscreenChanged = pyqtSignal()
    preset_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Музейные залы")
        self.setMinimumSize(800, 600)

        self.preset_manager = PresetManager()
        self.current_preset = None
        self.is_fullscreen = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        version_layout = QHBoxLayout()
        version_layout.addStretch()
        self.version_label = QLabel(f"Версия {VERSION}")
        self.version_label.setStyleSheet("color: #888888; font-size: 10px; padding: 5px; background: transparent;")
        version_layout.addWidget(self.version_label)
        self.layout.addLayout(version_layout)

        self.start_screen = StartScreen(self)
        self.hall_screen = HallSelectionScreen(self)

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.hall_screen)

        self.level_screens = {}

        self.start_screen.start_clicked.connect(self.show_hall_selection)
        self.start_screen.theme_changed.connect(self.apply_theme)
        self.start_screen.open_preset_manager_signal.connect(self.open_preset_manager)
        self.start_screen.fullscreen_toggled.connect(self.toggle_fullscreen)
        self.start_screen.exit_app_signal.connect(self.exit_app)

    def apply_theme(self, theme_name):
        if theme_name in THEMES:
            self.setStyleSheet(THEMES[theme_name])

    def set_current_preset(self, preset):
        self.current_preset = preset
        self.level_screens.clear()
        self.preset_changed.emit()

    def show_hall_selection(self):
        # Очищаем кэш экранов уровней, чтобы они пересоздались с новым состоянием
        self.level_screens.clear()
        self.stack.setCurrentWidget(self.hall_screen)

    def show_level(self, hall_name, level):
        key = (hall_name, level)
        if key not in self.level_screens:
            hall_class = HALL_CLASSES.get(hall_name)
            if hall_class is None:
                from dialogs import BaseHallLevel
                hall_class = BaseHallLevel

            total_levels = HALLS[hall_name]
            preset_data = None
            if self.current_preset and hall_name in self.current_preset.get("halls", {}):
                hall_preset = self.current_preset["halls"][hall_name]
                preset_data = {
                    "levels": hall_preset["levels"],
                    "correct_answers": hall_preset["correct_answers"]
                }
                total_levels = len(preset_data["levels"])

            level_screen = hall_class(self, hall_name, level, total_levels, preset_data)
            self.stack.addWidget(level_screen)
            self.level_screens[key] = level_screen
        self.stack.setCurrentWidget(self.level_screens[key])

    def show_hall_selection_from_level(self):
        self.level_screens.clear()
        self.stack.setCurrentWidget(self.hall_screen)

    def navigate_to(self, hall_name, level):
        if self.current_preset and hall_name in self.current_preset.get("halls", {}):
            max_level = len(self.current_preset["halls"][hall_name]["levels"])
        else:
            max_level = HALLS[hall_name]
        if 1 <= level <= max_level:
            self.show_level(hall_name, level)
        else:
            QMessageBox.warning(self, "Ошибка", f"Уровень {level} не существует в зале {hall_name}.")

    def open_preset_manager(self):
        dialog = PresetManagerDialog(self.preset_manager, self)
        dialog.exec_()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen
        self.fullscreenChanged.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def exit_app(self):
        QApplication.quit()


class StartScreen(QWidget):
    start_clicked = pyqtSignal()
    theme_changed = pyqtSignal(str)
    open_preset_manager_signal = pyqtSignal()
    fullscreen_toggled = pyqtSignal()
    exit_app_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("🎨 Музейные залы")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: #5D3A1A; margin-bottom: 10px;")
        layout.addWidget(title)

        layout.addStretch()

        self.start_btn = QPushButton("🚀 Начать игру")
        self.start_btn.setMinimumSize(300, 70)
        self.start_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_btn.setFont(QFont("Arial", 18, QFont.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB74D;
                border: none;
                border-radius: 35px;
                color: #5D3A1A;
                padding: 15px;
            }
            QPushButton:hover { background-color: #FFA726; }
            QPushButton:pressed { background-color: #F57C00; }
        """)
        self.start_btn.clicked.connect(self.on_start)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        settings_btn = QPushButton("⚙️ Настройки")
        settings_btn.setMinimumSize(180, 55)
        settings_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settings_btn.setFont(QFont("Arial", 30))
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 28px;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFE0B2; }
        """)
        settings_btn.clicked.connect(self.open_settings)

        preset_btn = QPushButton("📚 Управление пресетами")
        preset_btn.setMinimumSize(220, 55)
        preset_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        preset_btn.setFont(QFont("Arial", 11))
        preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 28px;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFE0B2; }
        """)
        preset_btn.clicked.connect(self.open_preset_editor)

        fullscreen_btn = QPushButton("🖥️ Полный экран")
        fullscreen_btn.setMinimumSize(180, 55)
        fullscreen_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fullscreen_btn.setFont(QFont("Arial", 11))
        fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 28px;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFE0B2; }
        """)
        fullscreen_btn.clicked.connect(lambda: self.fullscreen_toggled.emit())

        exit_btn = QPushButton("🚪 Выход")
        exit_btn.setMinimumSize(180, 55)
        exit_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        exit_btn.setFont(QFont("Arial", 11))
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 28px;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFE0B2; }
        """)
        exit_btn.clicked.connect(lambda: self.exit_app_signal.emit())

        bottom_layout.addStretch()
        bottom_layout.addWidget(settings_btn)
        bottom_layout.addWidget(preset_btn)
        bottom_layout.addWidget(fullscreen_btn)
        bottom_layout.addWidget(exit_btn)
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

    def on_start(self):
        self.start_clicked.emit()

    def open_settings(self):
        from theme_preview_dialog import ThemePreviewDialog
        dialog = ThemePreviewDialog(self)
        if dialog.exec_() and dialog.selected_theme:
            self.theme_changed.emit(dialog.selected_theme)

    def open_preset_editor(self):
        self.open_preset_manager_signal.emit()


class HallSelectionScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        self.title = QLabel("Выберите зал")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 24, QFont.Bold))
        self.title.setStyleSheet("color: #5D3A1A; margin-bottom: 20px;")
        self.main_layout.addWidget(self.title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.scroll_area)

        self.back_btn = QPushButton("◀ На главный экран")
        self.back_btn.setMinimumSize(250, 60)
        self.back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.back_btn.setFont(QFont("Arial", 12))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 30px;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFE0B2; }
        """)
        self.back_btn.clicked.connect(self.go_back)
        self.main_layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)

        self.buttons = []  # для обновления шрифтов

        if self.parent and hasattr(self.parent, 'fullscreenChanged'):
            self.parent.fullscreenChanged.connect(self.updateButtonFonts)
        if self.parent and hasattr(self.parent, 'preset_changed'):
            self.parent.preset_changed.connect(self.rebuild_halls_grid)

        self.rebuild_halls_grid()

    def rebuild_halls_grid(self):
        """Создаёт сетку со всеми 5 залами, для залов из пресета показывает их количество уровней, иначе 0."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Всегда показываем все залы из HALLS
        all_hall_names = list(HALLS.keys())

        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setContentsMargins(50, 0, 50, 0)

        hall_emojis = {
            "Зал внимания (Найди лишний)": "🔍",
            "Зал знакомства (Найди такую же)": "🤝",
            "Зал мастера (Подбери цвета по картинке)": "🎨",
            "Зал реставратора (Заплатки)": "🖌️",
            "Зал хранителя (Сортировка по коллекциям)": "🏛️"
        }
        hall_display_names = {
            "Зал внимания (Найди лишний)": ("Зал внимания", "(Найди лишний)"),
            "Зал знакомства (Найди такую же)": ("Зал знакомства", "(Найди такую же)"),
            "Зал мастера (Подбери цвета по картинке)": ("Зал мастера", "(Подбери цвета по картинке)"),
            "Зал реставратора (Заплатки)": ("Зал реставратора", "(Заплатки)"),
            "Зал хранителя (Сортировка по коллекциям)": ("Зал хранителя", "(Сортировка по коллекциям)")
        }

        row, col = 0, 0
        for hall_name in all_hall_names:
            card = QPushButton()
            card.setMinimumSize(300, 180)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            card.setStyleSheet("""
                QPushButton {
                    background-color: #FFF8E7;
                    border: 2px solid #FFB74D;
                    border-radius: 20px;
                    text-align: center;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #FFE0B2;
                    border: 2px solid #F57C00;
                }
                QPushButton:pressed {
                    background-color: #FFCC80;
                }
            """)
            emoji = hall_emojis.get(hall_name, "🎮")
            display = hall_display_names.get(hall_name, (hall_name, ""))

            # Определяем количество уровней для этого зала
            if self.parent and self.parent.current_preset and hall_name in self.parent.current_preset.get("halls", {}):
                levels_count = len(self.parent.current_preset["halls"][hall_name]["levels"])
                text = f"{emoji}\n\n{display[0]}\n{display[1]}\n\n📊 Уровней: {levels_count}"
            else:
                # Зал не настроен в пресете
                text = f"{emoji}\n\n{display[0]}\n{display[1]}\n\n❌ Не настроен"
            card.setText(text)
            card.setFont(QFont("Arial", 12))
            # При клике на не настроенный зал показываем предупреждение или ничего не делаем
            if self.parent and self.parent.current_preset and hall_name in self.parent.current_preset.get("halls", {}):
                card.clicked.connect(lambda checked, name=hall_name: self.select_hall(name))
            else:
                # Если зал не настроен, клик не должен ничего делать или показывать сообщение
                card.clicked.connect(lambda checked, name=hall_name: self.show_not_configured(name))
            grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        container_layout.addLayout(grid)
        self.scroll_area.setWidget(container)
        # Обновляем список кнопок для масштабирования шрифта
        self.buttons = []
        if hasattr(container, 'findChildren'):
            for child in container.findChildren(QPushButton):
                self.buttons.append(child)
        QTimer.singleShot(50, self.updateButtonFonts)

    def show_not_configured(self, hall_name):
        QMessageBox.information(self, "Зал не настроен", f"Зал «{hall_name}» не содержит уровней в текущем пресете.\nВыберите другой пресет или отредактируйте этот.")

    def updateButtonFonts(self):
        for btn in self.buttons:
            height = btn.height()
            font_size = max(12, min(int(height / 7), 32))
            font = QFont("Arial", font_size, QFont.Bold)
            btn.setFont(font)

    def resizeEvent(self, event):
        QTimer.singleShot(10, self.updateButtonFonts)
        super().resizeEvent(event)

    def showEvent(self, event):
        QTimer.singleShot(10, self.updateButtonFonts)
        super().showEvent(event)

    def select_hall(self, hall_name):
        if self.parent:
            self.parent.show_level(hall_name, 1)

    def go_back(self):
        if self.parent:
            self.parent.stack.setCurrentIndex(0)
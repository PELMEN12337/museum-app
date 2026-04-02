from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QGridLayout, QApplication, QSizePolicy
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
import os

HALL_CLASSES = {
    "Зал внимания (Найди лишний)": AttentionHallLevel,
    "Зал знакомства (Найди такую же)": FamiliarityHallLevel,
    "Зал мастера (Подбери цвета по картинке)": MasterHallLevel,
    "Зал реставратора (Заплатки)": RestorerHallLevel,
    "Зал хранителя (Сортировка по коллекциям)": KeeperHallLevel,
}

class MainWindow(QMainWindow):
    fullscreenChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Музейные залы")
        self.setMinimumSize(800, 600)

        self.preset_manager = PresetManager(os.path.dirname(os.path.abspath(__file__)))
        self.current_preset = None
        self.is_fullscreen = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

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

    def show_hall_selection(self):
        self.stack.setCurrentWidget(self.hall_screen)

    def show_level(self, hall_name, level):
        key = (hall_name, level)
        if key not in self.level_screens:
            hall_class = HALL_CLASSES.get(hall_name)
            if hall_class is None:
                from halls.base_hall import BaseHallLevel
                hall_class = BaseHallLevel
            total_levels = HALLS[hall_name]
            preset_data = None
            if self.current_preset and hall_name in self.current_preset.get("halls", {}):
                hall_preset = self.current_preset["halls"][hall_name]
                preset_data = {
                    "levels": hall_preset["levels"],
                    "correct_answers": hall_preset["correct_answers"]
                }
            level_screen = hall_class(self, hall_name, level, total_levels, preset_data)
            self.stack.addWidget(level_screen)
            self.level_screens[key] = level_screen
        self.stack.setCurrentWidget(self.level_screens[key])

    def show_hall_selection_from_level(self):
        self.stack.setCurrentWidget(self.hall_screen)

    def navigate_to(self, hall_name, level):
        if hall_name in HALLS and 1 <= level <= HALLS[hall_name]:
            self.show_level(hall_name, level)

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
        settings_btn.setFont(QFont("Arial", 11))
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
        self.buttons = []
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Выберите зал")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #5D3A1A; margin-bottom: 20px;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setContentsMargins(50, 0, 50, 0)

        hall_display_names = {
            "Зал внимания (Найди лишний)": ("Зал внимания", "(Найди лишний)"),
            "Зал знакомства (Найди такую же)": ("Зал знакомства", "(Найди такую же)"),
            "Зал мастера (Подбери цвета по картинке)": ("Зал мастера", "(Подбери цвета по картинке)"),
            "Зал реставратора (Заплатки)": ("Зал реставратора", "(Заплатки)"),
            "Зал хранителя (Сортировка по коллекциям)": ("Зал хранителя", "(Сортировка по коллекциям)")
        }

        hall_emojis = {
            "Зал внимания (Найди лишний)": "🔍",
            "Зал знакомства (Найди такую же)": "🤝",
            "Зал мастера (Подбери цвета по картинке)": "🎨",
            "Зал реставратора (Заплатки)": "🖌️",
            "Зал хранителя (Сортировка по коллекциям)": "🏛️"
        }

        row, col = 0, 0
        for hall_name in HALLS.keys():
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
            levels_count = HALLS[hall_name]
            text = f"{emoji}\n\n{display[0]}\n{display[1]}\n\n📊 Уровней: {levels_count}"
            card.setText(text)
            card.setFont(QFont("Arial", 12))
            card.clicked.connect(lambda checked, name=hall_name: self.select_hall(name))
            grid.addWidget(card, row, col)
            self.buttons.append(card)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        layout.addLayout(grid)
        layout.addStretch()

        back_btn = QPushButton("◀ На главный экран")
        back_btn.setMinimumSize(250, 60)
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        back_btn.setFont(QFont("Arial", 12))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 30px;
                color: #5D3A1A;
            }
            QPushButton:hover { background-color: #FFE0B2; }
        """)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        if self.parent and hasattr(self.parent, 'fullscreenChanged'):
            self.parent.fullscreenChanged.connect(self.updateButtonFonts)

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
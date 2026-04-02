import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea, QWidget, QLabel, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt
from preset_editor import PresetEditor

class PresetManagerDialog(QDialog):
    def __init__(self, preset_manager, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.parent_window = parent
        self.setWindowTitle("Управление пресетами")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)

        self.current_used_preset = None
        if parent and hasattr(parent, 'current_preset') and parent.current_preset:
            self.current_used_preset = parent.current_preset.get("name")

        main_layout = QVBoxLayout(self)

        title = QLabel("Мои пресеты")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(10)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)

        bottom_buttons = QHBoxLayout()
        create_btn = QPushButton("➕ Создать")
        create_btn.clicked.connect(self.create_preset)
        close_btn = QPushButton("✖ Закрыть")
        close_btn.clicked.connect(self.accept)
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(create_btn)
        bottom_buttons.addWidget(close_btn)
        bottom_buttons.addStretch()
        main_layout.addLayout(bottom_buttons)

        self.refresh_list()

    def refresh_list(self):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for idx, preset in enumerate(self.preset_manager.presets):
            panel = QWidget()
            is_selected = (self.current_used_preset == preset.get("name"))
            if is_selected:
                panel.setStyleSheet("""
                    QWidget {
                        background-color: #E8F0FE;
                        border-radius: 10px;
                        border: 2px solid #2196F3;
                        margin: 2px;
                    }
                """)
            else:
                panel.setStyleSheet("""
                    QWidget {
                        background-color: #FFF8E7;
                        border-radius: 10px;
                        margin: 2px;
                    }
                """)
            panel_layout = QHBoxLayout(panel)
            panel_layout.setContentsMargins(10, 5, 10, 5)

            name_label = QLabel(preset.get("name", f"Пресет {idx+1}"))
            name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            name_label.setWordWrap(True)
            name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            button_style = """
                QPushButton {
                    background-color: %s;
                    color: white;
                    font-size: 20px;
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                    min-width: 60px;
                    max-width: 60px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    opacity: 0.8;
                }
            """

            if is_selected:
                use_btn = QPushButton("☑️")
                use_btn.setToolTip("Используется в данный момент")
                use_btn.setStyleSheet(button_style % "#FFA500")
                use_btn.setEnabled(False)
            else:
                use_btn = QPushButton("▶")
                use_btn.setToolTip("Использовать пресет")
                use_btn.setStyleSheet(button_style % "#4CAF50")
                use_btn.clicked.connect(lambda checked, i=idx: self.use_preset(i))

            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setStyleSheet(button_style % "#2196F3")
            edit_btn.clicked.connect(lambda checked, i=idx: self.edit_preset(i))

            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Удалить")
            delete_btn.setStyleSheet(button_style % "#f44336")
            delete_btn.clicked.connect(lambda checked, i=idx: self.delete_preset(i))

            panel_layout.addWidget(name_label)
            panel_layout.addStretch()
            panel_layout.addWidget(use_btn)
            panel_layout.addWidget(edit_btn)
            panel_layout.addWidget(delete_btn)

            self.container_layout.addWidget(panel)

    def create_preset(self):
        editor = PresetEditor(self.preset_manager, self)
        if editor.exec_():
            self.refresh_list()

    def edit_preset(self, idx):
        preset = self.preset_manager.get_preset(idx)
        if preset:
            editor = PresetEditor(self.preset_manager, self, preset_data=preset, preset_index=idx)
            if editor.exec_():
                # Если редактируемый пресет является текущим в главном окне, обновляем его
                if self.parent_window and self.parent_window.current_preset and self.parent_window.current_preset.get("name") == preset.get("name"):
                    updated_preset = self.preset_manager.get_preset(idx)
                    self.parent_window.set_current_preset(updated_preset)
                self.refresh_list()

    def delete_preset(self, idx):
        reply = QMessageBox.question(self, "Подтверждение", "Удалить выбранный пресет?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            preset = self.preset_manager.get_preset(idx)
            self.preset_manager.remove_preset(idx)
            # Если удалили текущий используемый пресет, сбрасываем его в главном окне
            if preset and self.parent_window and self.parent_window.current_preset and self.parent_window.current_preset.get("name") == preset.get("name"):
                self.parent_window.set_current_preset(None)
            self.refresh_list()

    def use_preset(self, idx):
        preset = self.preset_manager.get_preset(idx)
        if preset and self.parent_window:
            self.parent_window.set_current_preset(preset)
            self.current_used_preset = preset.get("name")
            self.refresh_list()
            self.accept()
THEMES = {
    "Тёплая": """
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #F9F3E6, stop:1 #FFE4B5);
        }
        QWidget {
            font-family: "Comic Sans MS", "Segoe UI Emoji", cursive;
        }
        QPushButton {
            background-color: #FFB74D;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: #5D3A1A;
        }
        QPushButton:hover { background-color: #FFA726; }
        QPushButton:pressed { background-color: #F57C00; }
        QListWidget {
            background-color: #FFF8E7;
            border-radius: 15px;
            padding: 5px;
            font-size: 14px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background-color: #FFB74D;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #FFE0B2;
        }
        QLabel {
            color: #5D3A1A;
        }
    """,
    "Холодная": """
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #E6F0FA, stop:1 #C5E0F0);
        }
        QWidget {
            font-family: "Segoe UI", "Arial", sans-serif;
        }
        QPushButton {
            background-color: #4A90E2;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover { background-color: #357ABD; }
        QPushButton:pressed { background-color: #2C5E8C; }
        QListWidget {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 5px;
            font-size: 14px;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background-color: #4A90E2;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #D4E6F1;
        }
        QLabel {
            color: #2C3E50;
        }
    """,
    "Тёмная": """
        QMainWindow, QDialog {
            background-color: #2C2C2C;
        }
        QWidget {
            font-family: "Segoe UI", "Arial", sans-serif;
        }
        QPushButton {
            background-color: #3E3E3E;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: #E0E0E0;
        }
        QPushButton:hover { background-color: #505050; }
        QPushButton:pressed { background-color: #2C2C2C; }
        QListWidget {
            background-color: #3E3E3E;
            border-radius: 15px;
            padding: 5px;
            font-size: 14px;
            color: #E0E0E0;
        }
        QListWidget::item {
            padding: 8px;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background-color: #505050;
            color: white;
        }
        QListWidget::item:hover {
            background-color: #4A4A4A;
        }
        QLabel {
            color: #E0E0E0;
        }
    """,
    "Лесная": """
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #E8F5E9, stop:1 #C8E6C9);
        }
        QPushButton {
            background-color: #2E7D32;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover { background-color: #1B5E20; }
        QPushButton:pressed { background-color: #004D40; }
        QLabel { color: #1B5E20; }
    """,
    "Морская": """
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #E1F5FE, stop:1 #B3E5FC);
        }
        QPushButton {
            background-color: #0288D1;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover { background-color: #0277BD; }
        QPushButton:pressed { background-color: #01579B; }
        QLabel { color: #01579B; }
    """,
    "Космическая": """
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                         stop:0 #1A237E, stop:1 #283593);
        }
        QPushButton {
            background-color: #FFC107;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            color: #1A237E;
        }
        QPushButton:hover { background-color: #FFB300; }
        QPushButton:pressed { background-color: #FFA000; }
        QLabel { color: #FFECB3; }
    """
}
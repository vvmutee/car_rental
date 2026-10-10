from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import pyqtSignal, Qt


class HeaderBar(QFrame):
    """
    Верхняя панель приложения: заголовок + кнопки действий.
    Переопределяет QFrame.
    """

    action_triggered = pyqtSignal(str)  # сигнал при нажатии кнопки

    def __init__(self, title: str = "ПрокАвтомобилей",
                 parent: QWidget = None):
        super().__init__(parent)
        self._title = title
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setAlignment(Qt.AlignVCenter)

        # Логотип + заголовок
        logo = QLabel("🚗")
        logo.setStyleSheet("font-size: 24px;")
        layout.addWidget(logo, alignment=Qt.AlignLeft)

        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        layout.addWidget(self._title_label, alignment=Qt.AlignLeft)

        layout.addStretch()

        # Кнопки действий
        self._buttons = {}
        for action, icon in [("Новая аренда", "➕"), ("Клиенты", "👥"),
                              ("Авто", "🚙"), ("Отчет", "📊")]:
            btn = QPushButton(f"{icon} {action}")
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda checked, a=action: self.action_triggered.emit(a))
            layout.addWidget(btn, alignment=Qt.AlignRight)
            self._buttons[action] = btn

    def _apply_style(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            HeaderBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D2, stop:1 #2196F3);
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
            }
        """)
        self.setMinimumHeight(60)

    # --- Геттеры/сеттеры ---
    @property
    def title(self) -> str: return self._title
    @title.setter
    def title(self, value: str):
        self._title = value
        self._title_label.setText(value)

    # --- Спец. методы ---
    def __repr__(self):
        return f"<HeaderBar(title={self._title!r})>"

    def __str__(self):
        return f"Шапка: {self._title}"

    def __eq__(self, other):
        if isinstance(other, HeaderBar):
            return self._title == other._title
        return NotImplemented

    def __hash__(self):
        return hash(self._title)

    def __len__(self):
        return len(self._buttons)
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt


class StatusBadge(QLabel):
    """
    Цветной бейдж статуса.
    Переопределяет QLabel.
    """

    STATUS_COLORS = {
        "active": ("#e3f2fd", "#1976d2", "В работе"),
        "completed": ("#e8f5e9", "#388e3c", "Завершено"),
        "cancelled": ("#ffebee", "#d32f2f", "Отменено"),
        "overdue": ("#fff3e0", "#f57c00", "Просрочено"),
        "available": ("#e8f5e9", "#388e3c", "Доступно"),
        "rented": ("#e3f2fd", "#1976d2", "В аренде"),
        "maintenance": ("#fff3e0", "#f57c00", "На ТО"),
    }

    def __init__(self, status: str = "active", parent: QWidget = None):
        super().__init__(parent)
        self._status = status
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(26)
        self.update_status(status)

    # --- Геттеры/сеттеры ---
    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self.update_status(value)

    def update_status(self, status: str):
        if status not in self.STATUS_COLORS:
            raise ValueError(f"Неизвестный статус: {status}")
        self._status = status
        bg, fg, text = self.STATUS_COLORS[status]
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        self.adjustSize()

    # --- Спец. методы ---
    def __repr__(self):
        return f"<StatusBadge(status={self._status!r})>"

    def __str__(self):
        return self.STATUS_COLORS[self._status][2]

    def __eq__(self, other):
        if isinstance(other, StatusBadge):
            return self._status == other._status
        return NotImplemented

    def __hash__(self):
        return hash(self._status)

    def __lt__(self, other):
        if isinstance(other, StatusBadge):
            return self._status < other._status
        return NotImplemented
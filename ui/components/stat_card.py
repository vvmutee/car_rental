from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt


class StatCard(QFrame):
    """
    Карточка статистики: иконка + число + подпись.
    Переопределяет QFrame.
    """

    def __init__(self, title: str, value: str = "0", icon: str = "",
                 color: str = "#2196F3", parent: QWidget = None):
        super().__init__(parent)
        self._title = title
        self._value = value
        self._icon = icon
        self._color = color

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Создание и выравнивание компонентов внутри карточки."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)  # выравнивание по центру

        # Иконка
        self._icon_label = QLabel(self._icon)
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setStyleSheet(f"font-size: 28px; color: {self._color};")
        layout.addWidget(self._icon_label, alignment=Qt.AlignCenter)

        # Значение
        self._value_label = QLabel(self._value)
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #212121;")
        layout.addWidget(self._value_label, alignment=Qt.AlignCenter)

        # Подпись
        self._title_label = QLabel(self._title)
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet("font-size: 13px; color: #757575;")
        layout.addWidget(self._title_label, alignment=Qt.AlignCenter)

    def _apply_style(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            StatCard {{
                background: white;
                border: 1px solid #e0e0e0;
                border-left: 4px solid {self._color};
                border-radius: 8px;
            }}
        """)
        self.setMinimumSize(180, 120)

    # --- Геттеры/сеттеры ---
    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        self._title_label.setText(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, val: str):
        self._value = val
        self._value_label.setText(val)

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value
        self._apply_style()

    # --- Спец. методы ---
    def __repr__(self):
        return f"<StatCard(title={self._title!r}, value={self._value!r})>"

    def __str__(self):
        return f"{self._title}: {self._value}"

    def __eq__(self, other):
        if isinstance(other, StatCard):
            return self._title == other._title
        return NotImplemented

    def __hash__(self):
        return hash(self._title)

    def __lt__(self, other):
        if isinstance(other, StatCard):
            return self._title < other._title
        return NotImplemented
from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFocusEvent


class CustomLineEdit(QLineEdit):
    """
    Кастомное поле ввода с валидацией, плейсхолдером и сигналами.
    Переопределяет стандартный QLineEdit.
    """

    validation_changed = pyqtSignal(bool)  # сигнал при изменении валидности

    def __init__(self, placeholder: str = "", validator_type: str = "text",
                 parent: QWidget = None):
        super().__init__(parent)
        self._validator_type = validator_type
        self._is_valid = True

        # Настройка внешнего вида
        self.setPlaceholderText(placeholder)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setMinimumHeight(36)

        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QLineEdit[valid="false"] {
                border: 2px solid #f44336;
                background: #fff5f5;
            }
        """)

        # Подключаем сигналы
        self.textChanged.connect(self._on_text_changed)

    # --- Геттеры/сеттеры ---
    @property
    def validator_type(self) -> str:
        return self._validator_type

    @validator_type.setter
    def validator_type(self, value: str):
        allowed = {"text", "number", "phone", "email", "vin"}
        if value not in allowed:
            raise ValueError(f"Тип валидатора: {allowed}")
        self._validator_type = value
        self._on_text_changed(self.text())

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    # --- Валидация ---
    def _on_text_changed(self, text: str):
        old_valid = self._is_valid
        self._is_valid = self._validate(text)
        self.setProperty("valid", "true" if self._is_valid else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if old_valid != self._is_valid:
            self.validation_changed.emit(self._is_valid)

    def _validate(self, text: str) -> bool:
        if self._validator_type == "text":
            return len(text.strip()) >= 2
        elif self._validator_type == "number":
            return text.isdigit() or text == ""
        elif self._validator_type == "phone":
            digits = ''.join(c for c in text if c.isdigit())
            return len(digits) == 11 or text == ""
        elif self._validator_type == "email":
            return "@" in text and "." in text or text == ""
        elif self._validator_type == "vin":
            clean = text.upper().replace(' ', '')
            return len(clean) <= 17
        return True

    def validate(self) -> bool:
        """Публичный метод валидации."""
        return self._validate(self.text())

    # --- Переопределение событий ---
    def focusInEvent(self, event: QFocusEvent):
        super().focusInEvent(event)
        self.selectAll()

    # --- Спец. методы ---
    def __repr__(self):
        return f"<CustomLineEdit(placeholder={self.placeholderText()!r}, valid={self._is_valid})>"

    def __str__(self):
        return f"Поле ввода: {self.placeholderText()}"

    def __len__(self):
        return len(self.text())

    def __eq__(self, other):
        if isinstance(other, CustomLineEdit):
            return self.text() == other.text()
        return NotImplemented
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt


class MoneyLabel(QLabel):
    """
    Лейбл для отображения денег с форматированием.
    Переопределяет QLabel.
    """

    def __init__(self, amount: float = 0.0, currency: str = "₽",
                 parent: QWidget = None):
        super().__init__(parent)
        self._amount = amount
        self._currency = currency
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._update_text()
        self._apply_style()

    def _update_text(self):
        formatted = f"{self._amount:,.2f}".replace(",", " ")
        self.setText(f"{formatted} {self._currency}")

    def _apply_style(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2e7d32;
            }
        """)

    # --- Геттеры/сеттеры ---
    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Сумма >= 0")
        self._amount = float(value)
        self._update_text()

    @property
    def currency(self) -> str:
        return self._currency

    @currency.setter
    def currency(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Валюта не может быть пустой")
        self._currency = value.strip()
        self._update_text()

    # --- Спец. методы ---
    def __repr__(self):
        return f"<MoneyLabel(amount={self._amount}, currency={self._currency!r})>"

    def __str__(self):
        return f"{self._amount:,.2f} {self._currency}"

    def __eq__(self, other):
        if isinstance(other, MoneyLabel):
            return self._amount == other._amount
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, MoneyLabel):
            return self._amount < other._amount
        return NotImplemented

    def __hash__(self):
        return hash(self._amount)

    def __add__(self, other):
        if isinstance(other, MoneyLabel):
            return self._amount + other._amount
        return NotImplemented
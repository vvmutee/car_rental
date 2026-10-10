from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt
from ui.components.status_badge import StatusBadge
from ui.components.money_label import MoneyLabel


class RentalCard(QFrame):
    """
    Карточка аренды: клиент, авто, даты, статус, сумма.
    Переопределяет QFrame.
    """

    def __init__(self, customer_name: str, car_info: str,
                 start_date: str, end_date: str,
                 total_cost: float, status: str = "active",
                 parent: QWidget = None):
        super().__init__(parent)
        self._customer_name = customer_name
        self._car_info = car_info
        self._start_date = start_date
        self._end_date = end_date
        self._total_cost = total_cost
        self._status = status

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Создание и выравнивание компонентов."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # Верхняя строка: клиент + статус
        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignVCenter)

        self._customer_label = QLabel(f"👤 {self._customer_name}")
        self._customer_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        top_row.addWidget(self._customer_label, alignment=Qt.AlignLeft)

        top_row.addStretch()

        self._status_badge = StatusBadge(self._status)
        top_row.addWidget(self._status_badge, alignment=Qt.AlignRight)

        main_layout.addLayout(top_row)

        # Авто
        self._car_label = QLabel(f"🚗 {self._car_info}")
        self._car_label.setStyleSheet("font-size: 13px; color: #424242;")
        main_layout.addWidget(self._car_label, alignment=Qt.AlignLeft)

        # Даты
        self._dates_label = QLabel(f"📅 {self._start_date} — {self._end_date}")
        self._dates_label.setStyleSheet("font-size: 13px; color: #616161;")
        main_layout.addWidget(self._dates_label, alignment=Qt.AlignLeft)

        # Нижняя строка: сумма
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignVCenter)
        bottom_row.addStretch()

        self._money_label = MoneyLabel(self._total_cost)
        bottom_row.addWidget(self._money_label, alignment=Qt.AlignRight)

        main_layout.addLayout(bottom_row)

    def _apply_style(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            RentalCard {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            RentalCard:hover {
                border: 1px solid #2196F3;
            }
        """)

    # --- Геттеры/сеттеры ---
    @property
    def customer_name(self) -> str: return self._customer_name
    @customer_name.setter
    def customer_name(self, value: str):
        self._customer_name = value
        self._customer_label.setText(f"👤 {value}")

    @property
    def status(self) -> str: return self._status
    @status.setter
    def status(self, value: str):
        self._status = value
        self._status_badge.status = value

    @property
    def total_cost(self) -> float: return self._total_cost
    @total_cost.setter
    def total_cost(self, value: float):
        self._total_cost = value
        self._money_label.amount = value

    # --- Спец. методы ---
    def __repr__(self):
        return f"<RentalCard(customer={self._customer_name!r}, status={self._status})>"

    def __str__(self):
        return f"{self._customer_name} → {self._car_info}"

    def __eq__(self, other):
        if isinstance(other, RentalCard):
            return self._customer_name == other._customer_name
        return NotImplemented

    def __hash__(self):
        return hash(self._customer_name)

    def __lt__(self, other):
        if isinstance(other, RentalCard):
            return self._total_cost < other._total_cost
        return NotImplemented
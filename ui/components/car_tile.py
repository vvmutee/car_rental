from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt
from ui.components.status_badge import StatusBadge
from ui.components.money_label import MoneyLabel


class CarTile(QFrame):
    """
    Плитка автомобиля: бренд, модель, номер, статус, цена.
    Переопределяет QFrame.
    """

    def __init__(self, brand: str, model: str, license_plate: str,
                 year: int, status: str = "available",
                 price_per_day: float = 0.0, parent: QWidget = None):
        super().__init__(parent)
        self._brand = brand
        self._model = model
        self._license_plate = license_plate
        self._year = year
        self._status = status
        self._price_per_day = price_per_day

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Верх: бренд + модель
        header = QLabel(f"🚗 {self._brand} {self._model}")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #212121;")
        layout.addWidget(header, alignment=Qt.AlignLeft)

        # Номер и год
        info = QLabel(f"🔢 {self._license_plate}  •  📆 {self._year}")
        info.setStyleSheet("font-size: 12px; color: #757575;")
        layout.addWidget(info, alignment=Qt.AlignLeft)

        # Нижняя строка: статус + цена
        bottom = QHBoxLayout()
        bottom.setAlignment(Qt.AlignVCenter)

        self._status_badge = StatusBadge(self._status)
        bottom.addWidget(self._status_badge, alignment=Qt.AlignLeft)

        bottom.addStretch()

        self._money_label = MoneyLabel(self._price_per_day)
        bottom.addWidget(self._money_label, alignment=Qt.AlignRight)

        layout.addLayout(bottom)

    def _apply_style(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            CarTile {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            CarTile:hover {
                background: #f5f5f5;
                border: 1px solid #2196F3;
            }
        """)
        self.setMinimumSize(260, 110)

    # --- Геттеры/сеттеры ---
    @property
    def brand(self) -> str: return self._brand
    @brand.setter
    def brand(self, value: str): self._brand = value

    @property
    def status(self) -> str: return self._status
    @status.setter
    def status(self, value: str):
        self._status = value
        self._status_badge.status = value

    @property
    def price_per_day(self) -> float: return self._price_per_day
    @price_per_day.setter
    def price_per_day(self, value: float):
        self._price_per_day = value
        self._money_label.amount = value

    # --- Спец. методы ---
    def __repr__(self):
        return f"<CarTile({self._brand} {self._model} [{self._license_plate}])>"

    def __str__(self):
        return f"{self._brand} {self._model} [{self._license_plate}]"

    def __eq__(self, other):
        if isinstance(other, CarTile):
            return self._license_plate == other._license_plate
        return NotImplemented

    def __hash__(self):
        return hash(self._license_plate)

    def __lt__(self, other):
        if isinstance(other, CarTile):
            return self._price_per_day < other._price_per_day
        return NotImplemented
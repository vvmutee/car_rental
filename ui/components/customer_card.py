from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt


class CustomerCard(QFrame):
    """
    Карточка клиента: ФИО, телефон, ВУ.
    Переопределяет QFrame.
    """

    def __init__(self, full_name: str, phone: str, driver_license: str,
                 parent: QWidget = None):
        super().__init__(parent)
        self._full_name = full_name
        self._phone = phone
        self._driver_license = driver_license

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # ФИО
        self._name_label = QLabel(f"👤 {self._full_name}")
        self._name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #212121;")
        layout.addWidget(self._name_label, alignment=Qt.AlignLeft)

        # Телефон
        self._phone_label = QLabel(f"📞 {self._phone}")
        self._phone_label.setStyleSheet("font-size: 13px; color: #424242;")
        layout.addWidget(self._phone_label, alignment=Qt.AlignLeft)

        # ВУ
        self._license_label = QLabel(f"🪪 ВУ: {self._driver_license}")
        self._license_label.setStyleSheet("font-size: 13px; color: #616161;")
        layout.addWidget(self._license_label, alignment=Qt.AlignLeft)

    def _apply_style(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            CustomerCard {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            CustomerCard:hover {
                border: 1px solid #4CAF50;
            }
        """)
        self.setMinimumSize(280, 100)

    # --- Геттеры/сеттеры ---
    @property
    def full_name(self) -> str: return self._full_name
    @full_name.setter
    def full_name(self, value: str):
        self._full_name = value
        self._name_label.setText(f"👤 {value}")

    @property
    def phone(self) -> str: return self._phone
    @phone.setter
    def phone(self, value: str):
        self._phone = value
        self._phone_label.setText(f"📞 {value}")

    # --- Спец. методы ---
    def __repr__(self):
        return f"<CustomerCard(name={self._full_name!r})>"

    def __str__(self):
        return f"{self._full_name} ({self._phone})"

    def __eq__(self, other):
        if isinstance(other, CustomerCard):
            return self._full_name == other._full_name
        return NotImplemented

    def __hash__(self):
        return hash(self._full_name)

    def __lt__(self, other):
        if isinstance(other, CustomerCard):
            return self._full_name < other._full_name
        return NotImplemented
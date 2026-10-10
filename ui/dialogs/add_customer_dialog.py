from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QDateEdit, QFormLayout,
                              QMessageBox, QWidget)
from PyQt5.QtCore import Qt, QDate
from datetime import date


class AddCustomerDialog(QDialog):
    """Диалог добавления нового клиента."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить клиента")
        self.setMinimumWidth(400)
        self._customer_data = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("👤 Новый клиент")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Форма
        form = QFormLayout()
        form.setSpacing(10)

        # ФИО
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Иванов Иван Иванович")
        self._name_input.setMinimumHeight(32)
        form.addRow("ФИО:", self._name_input)

        # Паспорт
        self._passport_input = QLineEdit()
        self._passport_input.setPlaceholderText("1234567890")
        self._passport_input.setMinimumHeight(32)
        form.addRow("Паспорт:", self._passport_input)

        # Телефон
        self._phone_input = QLineEdit()
        self._phone_input.setPlaceholderText("+79991234567")
        self._phone_input.setMinimumHeight(32)
        form.addRow("Телефон:", self._phone_input)

        # Водительское удостоверение
        self._license_input = QLineEdit()
        self._license_input.setPlaceholderText("77АА123456")
        self._license_input.setMinimumHeight(32)
        form.addRow("Водительское удостоверение:", self._license_input)

        # Дата рождения
        self._birth_date_input = QDateEdit()
        self._birth_date_input.setCalendarPopup(True)
        self._birth_date_input.setDate(QDate(1990, 1, 1))
        self._birth_date_input.setMinimumHeight(32)
        form.addRow("Дата рождения:", self._birth_date_input)

        layout.addLayout(form)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self._cancel_btn = QPushButton("Отмена")
        self._cancel_btn.setMinimumHeight(36)
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)

        self._save_btn = QPushButton("Сохранить")
        self._save_btn.setMinimumHeight(36)
        self._save_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        self._save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self._save_btn)

        layout.addLayout(btn_layout)

    def _on_save(self):
        """Валидация и сохранение."""
        name = self._name_input.text().strip()
        passport = self._passport_input.text().strip()
        phone = self._phone_input.text().strip()
        license_num = self._license_input.text().strip()
        birth_date = self._birth_date_input.date().toPyDate()

        # Валидация
        if len(name) < 5:
            QMessageBox.warning(self, "Ошибка", "ФИО должно содержать минимум 5 символов")
            return

        if not passport.isdigit() or len(passport) != 10:
            QMessageBox.warning(self, "Ошибка", "Паспорт должен содержать 10 цифр")
            return

        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) != 11:
            QMessageBox.warning(self, "Ошибка", "Телефон должен содержать 11 цифр")
            return

        if len(license_num) < 10:
            QMessageBox.warning(self, "Ошибка", "Водительское удостоверение указано некорректно")
            return

        if birth_date >= date.today():
            QMessageBox.warning(self, "Ошибка", "Дата рождения должна быть в прошлом")
            return

        # Сохраняем данные
        self._customer_data = {
            'full_name': name,
            'passport': passport,
            'phone': f"+{digits}",
            'driver_license': license_num,
            'birth_date': birth_date
        }

        self.accept()

    def get_customer_data(self):
        """Возвращает данные клиента после успешного сохранения."""
        return self._customer_data
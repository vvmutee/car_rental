from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QDateEdit, QDoubleSpinBox,
                              QFormLayout, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from entity_storage.entity_collection import EntityCollection


class AddRentalDialog(QDialog):
    """Диалог создания новой аренды."""

    def __init__(self, customers: EntityCollection, cars: EntityCollection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Оформить аренду")
        self.setMinimumWidth(500)
        self._customers = customers
        self._cars = cars
        self._rental_data = None

        self._setup_ui()
        self._update_available_cars()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Оформление аренды")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Группа: Клиент
        client_group = QGroupBox("Клиент")
        client_layout = QFormLayout()

        self._customer_combo = QComboBox()
        self._customer_combo.setMinimumHeight(32)
        for customer in self._customers:
            self._customer_combo.addItem(f"{customer.full_name} ({customer.phone})", customer.id)
        client_layout.addRow("Выберите клиента:", self._customer_combo)

        new_client_btn = QPushButton("+ Новый клиент")
        new_client_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
        """)
        new_client_btn.clicked.connect(self._on_new_customer)
        client_layout.addRow("", new_client_btn)

        client_group.setLayout(client_layout)
        layout.addWidget(client_group)

        # Группа: Автомобиль
        car_group = QGroupBox("Автомобиль")
        car_layout = QFormLayout()

        self._car_combo = QComboBox()
        self._car_combo.setMinimumHeight(32)
        car_layout.addRow("Выберите автомобиль:", self._car_combo)

        car_group.setLayout(car_layout)
        layout.addWidget(car_group)

        # Группа: Даты и залог
        details_group = QGroupBox("Детали аренды")
        details_layout = QFormLayout()

        self._start_date = QDateEdit()
        self._start_date.setCalendarPopup(True)
        self._start_date.setDate(QDate.currentDate())
        self._start_date.setMinimumHeight(32)
        self._start_date.dateChanged.connect(self._calculate_cost)
        details_layout.addRow("Дата начала:", self._start_date)

        self._end_date = QDateEdit()
        self._end_date.setCalendarPopup(True)
        self._end_date.setDate(QDate.currentDate().addDays(3))
        self._end_date.setMinimumHeight(32)
        self._end_date.dateChanged.connect(self._calculate_cost)
        details_layout.addRow("Дата окончания:", self._end_date)

        self._deposit_spin = QDoubleSpinBox()
        self._deposit_spin.setRange(0, 100000)
        self._deposit_spin.setValue(5000)
        self._deposit_spin.setSuffix(" ₽")
        self._deposit_spin.setMinimumHeight(32)
        details_layout.addRow("Залог:", self._deposit_spin)

        self._cost_label = QLabel("0 ₽")
        self._cost_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        details_layout.addRow("Итого:", self._cost_label)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self._cancel_btn = QPushButton("Отмена")
        self._cancel_btn.setMinimumHeight(36)
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)

        self._save_btn = QPushButton("Оформить аренду")
        self._save_btn.setMinimumHeight(36)
        self._save_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        self._save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self._save_btn)

        layout.addLayout(btn_layout)

    def _update_available_cars(self):
        self._car_combo.clear()
        for car in self._cars:
            if car.is_available():
                self._car_combo.addItem(
                    f"{car.brand} {car.model} [{car.license_plate}] - {car.price_per_day:.0f} ₽/сутки",
                    car.id
                )

    def _on_new_customer(self):
        from ui.dialogs import AddCustomerDialog
        from entities import Customer

        dialog = AddCustomerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_customer_data()
            if data:
                customer = Customer(
                    full_name=data['full_name'],
                    passport=data['passport'],
                    phone=data['phone'],
                    driver_license=data['driver_license'],
                    birth_date=data['birth_date']
                )
                self._customers.add(customer)
                self._customer_combo.addItem(
                    f"{customer.full_name} ({customer.phone})",
                    customer.id
                )
                self._customer_combo.setCurrentIndex(self._customer_combo.count() - 1)

    def _calculate_cost(self):
        start = self._start_date.date().toPyDate()
        end = self._end_date.date().toPyDate()

        if end <= start:
            self._cost_label.setText("Ошибка: дата окончания должна быть позже начала")
            self._cost_label.setStyleSheet("font-size: 14px; color: #f44336;")
            return

        days = (end - start).days
        car_id = self._car_combo.currentData()

        if car_id:
            for car in self._cars:
                if car.id == car_id:
                    cost = car.calculate_rental_cost(days)
                    self._cost_label.setText(f"{cost:,.0f} ₽ ({days} дн.)")
                    self._cost_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
                    return

    def _on_save(self):
        customer_id = self._customer_combo.currentData()
        car_id = self._car_combo.currentData()
        start = self._start_date.date().toPyDate()
        end = self._end_date.date().toPyDate()
        deposit = self._deposit_spin.value()

        if not customer_id:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента")
            return

        if not car_id:
            QMessageBox.warning(self, "Ошибка", "Нет доступных автомобилей")
            return

        if end <= start:
            QMessageBox.warning(self, "Ошибка", "Дата окончания должна быть позже даты начала")
            return

        customer = None
        car = None
        for c in self._customers:
            if c.id == customer_id:
                customer = c
                break
        for car_obj in self._cars:
            if car_obj.id == car_id:
                car = car_obj
                break

        if not customer or not car:
            QMessageBox.warning(self, "Ошибка", "Клиент или автомобиль не найдены")
            return

        days = (end - start).days
        cost = car.calculate_rental_cost(days)

        self._rental_data = {
            'customer': customer,
            'car': car,
            'start_date': datetime.combine(start, datetime.min.time()),
            'end_date': datetime.combine(end, datetime.min.time()),
            'days': days,
            'total_cost': cost,
            'deposit': deposit
        }

        self.accept()

    def get_rental_data(self):
        return self._rental_data
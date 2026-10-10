from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QComboBox, QSpinBox,
                              QDoubleSpinBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from entity_storage.entity_collection import EntityCollection


class AddCarDialog(QDialog):
    """Диалог добавления нового автомобиля."""

    FUEL_TYPES = ["petrol", "diesel", "gas", "electric", "hybrid"]
    COLORS = ["белый", "чёрный", "серый", "синий", "красный", "зелёный", "серебристый"]

    def __init__(self, categories: EntityCollection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить автомобиль")
        self.setMinimumWidth(450)
        self._categories = categories
        self._car_data = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("🚗 Новый автомобиль")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Форма
        form = QFormLayout()
        form.setSpacing(10)

        # VIN
        self._vin_input = QLineEdit()
        self._vin_input.setPlaceholderText("XTAGFK1150Y654321")
        self._vin_input.setMinimumHeight(32)
        form.addRow("VIN:", self._vin_input)

        # Марка
        self._brand_input = QLineEdit()
        self._brand_input.setPlaceholderText("Lada")
        self._brand_input.setMinimumHeight(32)
        form.addRow("Марка:", self._brand_input)

        # Модель
        self._model_input = QLineEdit()
        self._model_input.setPlaceholderText("Vesta")
        self._model_input.setMinimumHeight(32)
        form.addRow("Модель:", self._model_input)

        # Гос. номер
        self._plate_input = QLineEdit()
        self._plate_input.setPlaceholderText("А123ВЕ777")
        self._plate_input.setMinimumHeight(32)
        form.addRow("Гос. номер:", self._plate_input)

        # Категория
        self._category_combo = QComboBox()
        self._category_combo.setMinimumHeight(32)
        for category in self._categories:
            self._category_combo.addItem(category.name, category.id)
        form.addRow("Категория:", self._category_combo)

        # Год
        self._year_spin = QSpinBox()
        self._year_spin.setRange(1990, 2026)
        self._year_spin.setValue(2022)
        self._year_spin.setMinimumHeight(32)
        form.addRow("Год:", self._year_spin)

        # Цвет
        self._color_combo = QComboBox()
        self._color_combo.addItems(self.COLORS)
        self._color_combo.setMinimumHeight(32)
        form.addRow("Цвет:", self._color_combo)

        # Тип топлива
        self._fuel_combo = QComboBox()
        self._fuel_combo.addItems(self.FUEL_TYPES)
        self._fuel_combo.setMinimumHeight(32)
        form.addRow("Тип топлива:", self._fuel_combo)

        # Пробег
        self._mileage_spin = QSpinBox()
        self._mileage_spin.setRange(0, 1000000)
        self._mileage_spin.setValue(0)
        self._mileage_spin.setMinimumHeight(32)
        form.addRow("Пробег (км):", self._mileage_spin)

        # Цена за сутки
        self._price_spin = QDoubleSpinBox()
        self._price_spin.setRange(100, 100000)
        self._price_spin.setValue(1500)
        self._price_spin.setSuffix(" ₽")
        self._price_spin.setMinimumHeight(32)
        form.addRow("Цена за сутки:", self._price_spin)

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
        vin = self._vin_input.text().strip().upper()
        brand = self._brand_input.text().strip()
        model = self._model_input.text().strip()
        plate = self._plate_input.text().strip().upper()
        category_id = self._category_combo.currentData()
        year = self._year_spin.value()
        color = self._color_combo.currentText()
        fuel = self._fuel_combo.currentText()
        mileage = self._mileage_spin.value()
        price = self._price_spin.value()

        # Валидация
        if len(vin) != 17:
            QMessageBox.warning(self, "Ошибка", "VIN должен содержать 17 символов")
            return

        if not brand:
            QMessageBox.warning(self, "Ошибка", "Марка не может быть пустой")
            return

        if not model:
            QMessageBox.warning(self, "Ошибка", "Модель не может быть пустой")
            return

        if len(plate) < 9:
            QMessageBox.warning(self, "Ошибка", "Гос. номер указан некорректно")
            return

        if not category_id:
            QMessageBox.warning(self, "Ошибка", "Категория не выбрана")
            return

        # Сохраняем данные
        self._car_data = {
            'vin': vin,
            'brand': brand,
            'model': model,
            'license_plate': plate,
            'category_id': category_id,
            'year': year,
            'color': color,
            'fuel_type': fuel,
            'mileage': mileage,
            'price_per_day': price
        }

        self.accept()

    def get_car_data(self):
        """Возвращает данные автомобиля после успешного сохранения."""
        return self._car_data
from entities.abstract_entity import AbstractEntity
from datetime import datetime
from functools import total_ordering
import re


from object_map import ObjectMap
class CarStatus:
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    WRITTEN_OFF = "written_off"


@total_ordering
class Car(AbstractEntity):
    """Автомобиль в парке проката."""

    def __init__(self, vin: str, brand: str, model: str, license_plate: str,
                 category_id: str, year: int, color: str, fuel_type: str,
                 mileage: int = 0, price_per_day: float = 0.0,
                 status: str = CarStatus.AVAILABLE,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.vin = vin
        self.brand = brand
        self.model = model
        self.license_plate = license_plate
        self.category_id = category_id
        self.year = year
        self.color = color
        self.fuel_type = fuel_type
        self.mileage = mileage
        self.price_per_day = price_per_day
        self.status = status

    # --- Геттеры ---
    @property
    def vin(self) -> str: return self._vin
    @property
    def brand(self) -> str: return self._brand
    @property
    def model(self) -> str: return self._model
    @property
    def license_plate(self) -> str: return self._license_plate
    @property
    def category_id(self) -> str: return self._category_id
    @property
    def year(self) -> int: return self._year
    @property
    def color(self) -> str: return self._color
    @property
    def fuel_type(self) -> str: return self._fuel_type
    @property
    def mileage(self) -> int: return self._mileage
    @property
    def price_per_day(self) -> float: return self._price_per_day
    @property
    def status(self) -> str: return self._status

    # --- Сеттеры ---
    @vin.setter
    def vin(self, value: str):
        value = value.strip().upper().replace(' ', '')
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', value):
            raise ValueError("VIN: 17 символов (без I, O, Q)")
        self._vin = value
        self.updated_at = datetime.now()

    @brand.setter
    def brand(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Марка не может быть пустой")
        self._brand = value.strip().title()
        self.updated_at = datetime.now()

    @model.setter
    def model(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Модель не может быть пустой")
        self._model = value.strip()
        self.updated_at = datetime.now()

    @license_plate.setter
    def license_plate(self, value: str):
        value = value.strip().upper().replace(' ', '')
        if not re.match(r'^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$', value):
            raise ValueError("Номер формата: А123БВ77 или А123БВ777")
        self._license_plate = value
        self.updated_at = datetime.now()

    @category_id.setter
    def category_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("category_id обязателен")
        self._category_id = value
        self.updated_at = datetime.now()

    @year.setter
    def year(self, value: int):
        if not isinstance(value, int) or not (1990 <= value <= datetime.now().year + 1):
            raise ValueError(f"Год: 1990..{datetime.now().year + 1}")
        self._year = value
        self.updated_at = datetime.now()

    @color.setter
    def color(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Цвет не может быть пустым")
        self._color = value.strip().lower()
        self.updated_at = datetime.now()

    @fuel_type.setter
    def fuel_type(self, value: str):
        allowed = {"petrol", "diesel", "gas", "electric", "hybrid"}
        if value.lower() not in allowed:
            raise ValueError(f"Тип топлива: {allowed}")
        self._fuel_type = value.lower()
        self.updated_at = datetime.now()

    @mileage.setter
    def mileage(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Пробег >= 0")
        self._mileage = value
        self.updated_at = datetime.now()

    @price_per_day.setter
    def price_per_day(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Цена >= 0")
        self._price_per_day = float(value)
        self.updated_at = datetime.now()

    @status.setter
    def status(self, value: str):
        allowed = {CarStatus.AVAILABLE, CarStatus.RENTED,
                   CarStatus.MAINTENANCE, CarStatus.WRITTEN_OFF}
        if value not in allowed:
            raise ValueError(f"Статус: {allowed}")
        self._status = value
        self.updated_at = datetime.now()

    # --- Бизнес-методы ---
    def calculate_rental_cost(self, days: int) -> float:
        if days <= 0:
            raise ValueError("Дней должно быть > 0")
        return self.price_per_day * days

    def is_available(self) -> bool:
        return self._status == CarStatus.AVAILABLE

    def mark_rented(self):
        self.status = CarStatus.RENTED

    def mark_available(self):
        self.status = CarStatus.AVAILABLE

    def mark_maintenance(self):
        self.status = CarStatus.MAINTENANCE

    def add_mileage(self, km: int):
        if km < 0:
            raise ValueError("km >= 0")
        self.mileage = self._mileage + km

    @staticmethod
    def decode_vin_region(vin: str) -> str:
        """Статический метод: определение региона производства по VIN."""
        if not vin or len(vin) < 1:
            return "unknown"
        first = vin[0].upper()
        mapping = {
            'S': 'Europe (UK/Spain)', 'Z': 'Italy', 'W': 'Germany',
            'V': 'France/Spain', 'J': 'Japan', 'K': 'Korea',
            'L': 'China', '1': 'USA', '2': 'Canada', '5': 'USA'
        }
        return mapping.get(first, 'other')

    # --- Валидация ---
    def validate(self) -> bool:
        return all([
            re.match(r'^[A-HJ-NPR-Z0-9]{17}$', self._vin),
            bool(self._brand),
            bool(self._model),
            re.match(r'^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}$', self._license_plate),
            bool(self._category_id),
            1990 <= self._year <= datetime.now().year + 1,
            self._mileage >= 0,
            self._price_per_day >= 0,
            self._status in {CarStatus.AVAILABLE, CarStatus.RENTED,
                             CarStatus.MAINTENANCE, CarStatus.WRITTEN_OFF},
        ])

    # --- Сериализация ---
    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Car'), ('id', self._id), ('vin', self._vin), ('brand', self._brand), ('model', self._model), ('license_plate', self._license_plate), ('category_id', self._category_id), ('year', self._year), ('color', self._color), ('fuel_type', self._fuel_type), ('mileage', self._mileage), ('price_per_day', self._price_per_day), ('status', self._status), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Car':
        return cls(
            vin=data['vin'], brand=data['brand'], model=data['model'],
            license_plate=data['license_plate'], category_id=data['category_id'],
            year=data['year'], color=data['color'], fuel_type=data['fuel_type'],
            mileage=data.get('mileage', 0), price_per_day=data.get('price_per_day', 0.0),
            status=data.get('status', CarStatus.AVAILABLE),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    # --- Спец. методы ---
    def __eq__(self, other):
        if isinstance(other, Car):
            return self._vin == other._vin
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Car):
            return self._mileage < other._mileage  # сортировка по пробегу
        return NotImplemented

    def __hash__(self):
        return hash(self._vin)

    def __repr__(self):
        return f"<Car(vin={self._vin!r}, {self._brand} {self._model})>"

    def __str__(self):
        return f"{self._brand} {self._model} [{self._license_plate}] — {self._price_per_day} ₽/сутки"

    def __mul__(self, days: int) -> float:
        """car * days = стоимость аренды."""
        if isinstance(days, int) and days > 0:
            return self.calculate_rental_cost(days)
        return NotImplemented

    def __add__(self, km: int) -> 'Car':
        """car + km = увеличение пробега."""
        if isinstance(km, int) and km >= 0:
            new_car = Car.from_dict(self.to_dict())
            new_car.mileage = self._mileage + km
            return new_car
        return NotImplemented
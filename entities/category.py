from entities.abstract_entity import AbstractEntity
from datetime import datetime
from functools import total_ordering


from object_map import ObjectMap
@total_ordering
class Category(AbstractEntity):
    """Категория автомобиля: эконом, комфорт, бизнес, внедорожник."""

    def __init__(self, name: str, deposit: float, min_driver_age: int,
                 price_per_day: float, entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.name = name
        self.deposit = deposit
        self.min_driver_age = min_driver_age
        self.price_per_day = price_per_day

    # --- Геттеры ---
    @property
    def name(self) -> str:
        return self._name

    @property
    def deposit(self) -> float:
        return self._deposit

    @property
    def min_driver_age(self) -> int:
        return self._min_driver_age

    @property
    def price_per_day(self) -> float:
        return self._price_per_day

    # --- Сеттеры с валидацией ---
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Название категории не может быть пустым")
        self._name = value.strip().title()
        self.updated_at = datetime.now()

    @deposit.setter
    def deposit(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Залог должен быть >= 0")
        self._deposit = float(value)
        self.updated_at = datetime.now()

    @min_driver_age.setter
    def min_driver_age(self, value: int):
        if not isinstance(value, int) or not (18 <= value <= 80):
            raise ValueError("Возраст водителя: 18-80")
        self._min_driver_age = value
        self.updated_at = datetime.now()

    @price_per_day.setter
    def price_per_day(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Цена за сутки должна быть > 0")
        self._price_per_day = float(value)
        self.updated_at = datetime.now()

    # --- Бизнес-логика ---
    def calculate_rental_cost(self, days: int) -> float:
        """Расчет стоимости аренды."""
        if days <= 0:
            raise ValueError("Количество дней должно быть > 0")
        return self.price_per_day * days

    # --- Валидация ---
    def validate(self) -> bool:
        return (bool(self._name) and
                self._deposit >= 0 and
                18 <= self._min_driver_age <= 80 and
                self._price_per_day > 0)

    # --- Сериализация ---
    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Category'), ('id', self._id), ('name', self._name), ('deposit', self._deposit), ('min_driver_age', self._min_driver_age), ('price_per_day', self._price_per_day), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Category':
        return cls(
            name=data['name'],
            deposit=data['deposit'],
            min_driver_age=data['min_driver_age'],
            price_per_day=data['price_per_day'],
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    # --- Спец. методы (дополнительно к базовым) ---
    def __eq__(self, other):
        if isinstance(other, Category):
            return self._name.lower() == other._name.lower()
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Category):
            return self._price_per_day < other._price_per_day
        return NotImplemented

    def __hash__(self):
        return hash(self._name.lower())

    def __repr__(self):
        return f"<Category(name={self._name!r}, price={self._price_per_day})>"

    def __str__(self):
        return f"{self._name} — {self._price_per_day} ₽/сутки"

    def __add__(self, other):
        """Сложение категорий = общая стоимость аренды двух."""
        if isinstance(other, Category):
            return self._price_per_day + other._price_per_day
        return NotImplemented
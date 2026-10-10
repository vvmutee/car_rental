from entities.abstract_entity import AbstractEntity
from datetime import datetime, date
from functools import total_ordering
import re


from object_map import ObjectMap
@total_ordering
class Customer(AbstractEntity):
    """Клиент проката."""

    def __init__(self, full_name: str, passport: str, phone: str,
                 driver_license: str, birth_date: date,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.full_name = full_name
        self.passport = passport
        self.phone = phone
        self.driver_license = driver_license
        self.birth_date = birth_date

    # --- Геттеры ---
    @property
    def full_name(self) -> str: return self._full_name
    @property
    def passport(self) -> str: return self._passport
    @property
    def phone(self) -> str: return self._phone
    @property
    def driver_license(self) -> str: return self._driver_license
    @property
    def birth_date(self) -> date: return self._birth_date

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self._birth_date.year - (
            (today.month, today.day) < (self._birth_date.month, self._birth_date.day)
        )

    # --- Сеттеры с валидацией ---
    @full_name.setter
    def full_name(self, value: str):
        if not isinstance(value, str) or len(value.strip()) < 5:
            raise ValueError("ФИО должно содержать минимум 5 символов")
        self._full_name = value.strip().title()
        self.updated_at = datetime.now()

    @passport.setter
    def passport(self, value: str):
        value = value.strip().replace(' ', '')
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Паспорт: 10 цифр")
        self._passport = value
        self.updated_at = datetime.now()

    @phone.setter
    def phone(self, value: str):
        digits = re.sub(r'\D', '', value)
        if len(digits) != 11:
            raise ValueError("Телефон: 11 цифр")
        self._phone = f"+{digits}"
        self.updated_at = datetime.now()

    @driver_license.setter
    def driver_license(self, value: str):
        value = value.strip().replace(' ', '')
        if not re.match(r'^\d{2}АА\d{6}$', value, re.IGNORECASE):
            raise ValueError("ВУ формата: 77АА123456")
        self._driver_license = value.upper()
        self.updated_at = datetime.now()

    @birth_date.setter
    def birth_date(self, value: date):
        if not isinstance(value, date):
            raise TypeError("birth_date должен быть datetime.date")
        if value >= date.today():
            raise ValueError("Дата рождения должна быть в прошлом")
        self._birth_date = value
        self.updated_at = datetime.now()

    # --- Бизнес-логика ---
    def can_rent_category(self, category) -> bool:
        """Проверка, может ли клиент арендовать авто данной категории."""
        return self.age >= category.min_driver_age

    def validate(self) -> bool:
        return all([
            len(self._full_name) >= 5,
            re.match(r'^\d{10}$', self._passport),
            len(re.sub(r'\D', '', self._phone)) == 11,
            re.match(r'^\d{2}АА\d{6}$', self._driver_license, re.IGNORECASE),
            self._birth_date < date.today(),
        ])

    # --- Сериализация ---
    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Customer'), ('id', self._id), ('full_name', self._full_name), ('passport', self._passport), ('phone', self._phone), ('driver_license', self._driver_license), ('birth_date', self._birth_date.isoformat()), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Customer':
        return cls(
            full_name=data['full_name'],
            passport=data['passport'],
            phone=data['phone'],
            driver_license=data['driver_license'],
            birth_date=date.fromisoformat(data['birth_date']),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    # --- Спец. методы ---
    def __eq__(self, other):
        if isinstance(other, Customer):
            return self._passport == other._passport
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Customer):
            return self._full_name < other._full_name
        return NotImplemented

    def __hash__(self):
        return hash(self._passport)

    def __repr__(self):
        return f"<Customer(name={self._full_name!r}, passport={self._passport})>"

    def __str__(self):
        return f"{self._full_name} (паспорт: {self._passport})"
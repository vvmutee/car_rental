"""
Сущность: Точка выдачи автомобилей.
"""

from entities.abstract_entity import AbstractEntity
from datetime import datetime
from functools import total_ordering
import re


from object_map import ObjectMap
@total_ordering
class Location(AbstractEntity):
    """Точка выдачи автомобилей."""

    def __init__(self, address: str, phone: str, work_hours: str,
                 latitude: float = 0.0, longitude: float = 0.0,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.address = address
        self.phone = phone
        self.work_hours = work_hours
        self.latitude = latitude
        self.longitude = longitude

    @property
    def address(self) -> str: return self._address
    @property
    def phone(self) -> str: return self._phone
    @property
    def work_hours(self) -> str: return self._work_hours
    @property
    def latitude(self) -> float: return self._latitude
    @property
    def longitude(self) -> float: return self._longitude

    @address.setter
    def address(self, value: str):
        if not isinstance(value, str) or len(value.strip()) < 5:
            raise ValueError("Адрес >= 5 символов")
        self._address = value.strip().title()
        self.updated_at = datetime.now()

    @phone.setter
    def phone(self, value: str):
        digits = re.sub(r'\D', '', value)
        if len(digits) != 11:
            raise ValueError("Телефон: 11 цифр")
        self._phone = f"+{digits}"
        self.updated_at = datetime.now()

    @work_hours.setter
    def work_hours(self, value: str):
        if not re.match(r'^\d{2}:\d{2}-\d{2}:\d{2}$', value.strip()):
            raise ValueError("Формат: 09:00-21:00")
        self._work_hours = value.strip()
        self.updated_at = datetime.now()

    @latitude.setter
    def latitude(self, value: float):
        if not isinstance(value, (int, float)) or not (-90 <= value <= 90):
            raise ValueError("Широта: -90..90")
        self._latitude = float(value)
        self.updated_at = datetime.now()

    @longitude.setter
    def longitude(self, value: float):
        if not isinstance(value, (int, float)) or not (-180 <= value <= 180):
            raise ValueError("Долгота: -180..180")
        self._longitude = float(value)
        self.updated_at = datetime.now()

    def validate(self) -> bool:
        return all([
            len(self._address) >= 5,
            len(re.sub(r'\D', '', self._phone)) == 11,
            re.match(r'^\d{2}:\d{2}-\d{2}:\d{2}$', self._work_hours),
            -90 <= self._latitude <= 90,
            -180 <= self._longitude <= 180,
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Location'), ('id', self._id), ('address', self._address), ('phone', self._phone), ('work_hours', self._work_hours), ('latitude', self._latitude), ('longitude', self._longitude), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Location':
        return cls(
            address=data['address'], phone=data['phone'],
            work_hours=data['work_hours'],
            latitude=data.get('latitude', 0.0),
            longitude=data.get('longitude', 0.0),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    def __eq__(self, other):
        if isinstance(other, Location):
            return self._address == other._address
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Location):
            return self._address < other._address
        return NotImplemented

    def __hash__(self):
        return hash(self._address)

    def __repr__(self):
        return f"<Location(address={self._address!r})>"

    def __str__(self):
        return f"{self._address} ({self._work_hours})"
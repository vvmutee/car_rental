from abc import ABC, abstractmethod
from datetime import datetime
import uuid
from object_map import ObjectMap


class AbstractEntity(ABC):
    """Базовый абстрактный класс для всех сущностей приложения."""

    def __init__(self, entity_id: str = None, created_at: datetime = None):
        self._id = entity_id or str(uuid.uuid4())
        self._created_at = created_at or datetime.now()
        self._updated_at = self._created_at

    # --- Геттеры ---
    @property
    def id(self) -> str:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("created_at must be datetime")
        self._created_at = value
        if self._updated_at < value:
            self._updated_at = value

    @id.setter
    def id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("id must be a non-empty string")
        self._id = value.strip()

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # --- Сеттер для updated_at ---
    @updated_at.setter
    def updated_at(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("updated_at must be datetime")
        self._updated_at = value

    # --- Абстрактные методы (обязательные для наследников) ---
    @abstractmethod
    def validate(self) -> bool:
        """Валидация сущности перед сохранением."""
        pass

    @abstractmethod
    def to_dict(self) -> ObjectMap:
        """Сериализация в словарь для JSON."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """Десериализация из словаря."""
        pass

    # --- Специальные методы (требование задания) ---
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self._id!r})>"

    def __str__(self):
        return f"{self.__class__.__name__} #{self._id[:8]}"

    def __lt__(self, other):
        """Сравнение по дате создания (для сортировки)."""
        if not isinstance(other, self.__class__):
            raise TypeError(f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}")
        return self._created_at < other._created_at
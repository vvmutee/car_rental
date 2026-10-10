from typing import TypeVar, Generic, Iterator, Callable, List, Optional
from entities.abstract_entity import AbstractEntity

T = TypeVar('T', bound=AbstractEntity)


class EntityCollection(Generic[T]):
    """
    Кастомная коллекция для хранения сущностей.
    ЗАМЕНА dict — согласно требованию задания.
    Поддерживает: add, get, remove, filter, find, iteration.
    """

    def __init__(self):
        self._items: List[T] = []

    # --- Основные методы ---
    def add(self, entity: T) -> None:
        if not isinstance(entity, AbstractEntity):
            raise TypeError("Можно добавлять только объекты AbstractEntity")
        if self.find_by_id(entity.id) is not None:
            raise ValueError(f"Сущность с id={entity.id} уже существует")
        self._items.append(entity)

    def get_by_id(self, entity_id: str) -> Optional[T]:
        return self.find_by_id(entity_id)

    def find_by_id(self, entity_id: str) -> Optional[T]:
        for item in self._items:
            if item.id == entity_id:
                return item
        return None

    def find(self, predicate: Callable[[T], bool]) -> Optional[T]:
        for item in self._items:
            if predicate(item):
                return item
        return None

    def filter(self, predicate: Callable[[T], bool]) -> 'EntityCollection[T]':
        result = EntityCollection()
        for item in self._items:
            if predicate(item):
                result.add(item)
        return result

    def remove(self, entity_id: str) -> bool:
        for i, item in enumerate(self._items):
            if item.id == entity_id:
                self._items.pop(i)
                return True
        return False

    def update(self, entity: T) -> bool:
        for i, item in enumerate(self._items):
            if item.id == entity.id:
                self._items[i] = entity
                return True
        return False

    # --- Свойства ---
    @property
    def count(self) -> int:
        return len(self._items)

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0

    def all(self) -> List[T]:
        return list(self._items)

    def first(self) -> Optional[T]:
        return self._items[0] if self._items else None

    def sorted_by(self, key: Callable[[T], any], reverse: bool = False) -> 'EntityCollection[T]':
        result = EntityCollection()
        for item in sorted(self._items, key=key, reverse=reverse):
            result.add(item)
        return result

    # --- Специальные методы ---
    def __len__(self):
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __contains__(self, entity: T) -> bool:
        return self.find_by_id(entity.id) is not None

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __repr__(self):
        return f"EntityCollection(count={self.count})"

    def __str__(self):
        return f"Коллекция [{self.count} объектов]: {', '.join(str(i) for i in self._items[:3])}{'...' if self.count > 3 else ''}"
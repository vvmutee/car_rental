import json
import os
from typing import Any
from datetime import datetime
from collections.abc import Mapping

from entities.abstract_entity import AbstractEntity
from entities.category import Category
from entities.customer import Customer
from entities.car import Car
from entities.employee import Employee
from entities.location import Location
from entities.insurance import Insurance
from entities.payment import Payment
from entities.rental import Rental
from entities.damage_report import DamageReport
from entities.maintenance import Maintenance
from entity_storage.entity_collection import EntityCollection
from object_map import ObjectMap


class StorageService:
    """
    Сервис для сохранения/загрузки данных в JSON.
    Использует кастомную коллекцию EntityCollection вместо dict.
    """

    # Пользовательское отображение типа сущности на класс.
    TYPE_TO_CLASS = ObjectMap([
        ('Category', Category), ('Customer', Customer), ('Car', Car),
        ('Employee', Employee), ('Location', Location), ('Insurance', Insurance),
        ('Payment', Payment), ('Rental', Rental), ('DamageReport', DamageReport),
        ('Maintenance', Maintenance),
    ])

    # Имена коллекций в JSON
    COLLECTION_NAMES = [
        'categories', 'customers', 'cars', 'employees', 'locations',
        'insurances', 'payments', 'rentals', 'damage_reports', 'maintenances'
    ]

    def __init__(self, filepath: str = "data.json"):
        self._filepath = filepath

    @property
    def filepath(self) -> str:
        return self._filepath

    @filepath.setter
    def filepath(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Путь к файлу не может быть пустым")
        self._filepath = value.strip()

    # --- Основной метод сохранения ---
    def save_all(self, data: ObjectMap) -> bool:
        """
        Сохраняет все коллекции в JSON.
        data: ObjectMap с коллекциями сущностей по именам.
        """
        try:
            payload = {
                'meta': {
                    'version': '1.0',
                    'saved_at': datetime.now().isoformat(),
                    'app': 'CarRental'
                },
                'data': {}
            }

            for collection_name in self.COLLECTION_NAMES:
                collection = data.get(collection_name)
                if collection is None:
                    payload['data'][collection_name] = []
                    continue

                items = []
                for entity in collection:
                    items.append(self._to_json_value(entity.to_dict()))
                payload['data'][collection_name] = items

            # Атомарная запись: сначала в tmp, потом rename
            tmp_path = self._filepath + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            if os.path.exists(self._filepath):
                os.remove(self._filepath)
            os.rename(tmp_path, self._filepath)

            return True

        except Exception as e:
            print(f"[StorageService] Ошибка сохранения: {e}")
            return False

    @classmethod
    def _to_json_value(cls, value):
        """Преобразует пользовательские отображения в JSON-совместимые объекты.

        Встроенные словари создаются только на границе JSON-сериализации,
        чтобы сохранить прежний формат data.json.
        """
        if isinstance(value, Mapping):
            return {key: cls._to_json_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._to_json_value(item) for item in value]
        return value

    # --- Основной метод загрузки ---
    def load_all(self) -> ObjectMap:
        """
        Загружает все коллекции из JSON.
        Возвращает ObjectMap с коллекциями сущностей.
        """
        result = ObjectMap((name, EntityCollection()) for name in self.COLLECTION_NAMES)

        if not os.path.exists(self._filepath):
            print(f"[StorageService] Файл {self._filepath} не найден. Созданы пустые коллекции.")
            return result

        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                payload = json.load(f)

            data = payload.get('data', {})

            for collection_name in self.COLLECTION_NAMES:
                items = data.get(collection_name, [])
                collection = result[collection_name]

                for item in items:
                    entity = self._deserialize_entity(item)
                    if entity is not None:
                        collection.add(entity)

            return result

        except json.JSONDecodeError as e:
            print(f"[StorageService] Ошибка парсинга JSON: {e}")
            return result
        except Exception as e:
            print(f"[StorageService] Ошибка загрузки: {e}")
            return result

    # --- Фабрика десериализации ---
    def _deserialize_entity(self, item: Mapping) -> AbstractEntity:
        """Восстанавливает объект из отображения, прочитанного JSON-парсером."""
        if not isinstance(item, Mapping) or 'type' not in item:
            return None

        entity_type = item['type']
        cls = self.TYPE_TO_CLASS.get(entity_type)

        if cls is None:
            print(f"[StorageService] Неизвестный тип: {entity_type}")
            return None

        try:
            return cls.from_dict(item)
        except Exception as e:
            print(f"[StorageService] Ошибка восстановления {entity_type}: {e}")
            return None

    # --- Вспомогательные методы ---
    def backup(self) -> str:
        """Создает резервную копию файла."""
        if not os.path.exists(self._filepath):
            return ""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self._filepath}.backup_{timestamp}"
        with open(self._filepath, 'r', encoding='utf-8') as src:
            content = src.read()
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        return backup_path

    def exists(self) -> bool:
        return os.path.exists(self._filepath)

    def clear(self) -> bool:
        """Удаляет файл данных."""
        try:
            if os.path.exists(self._filepath):
                os.remove(self._filepath)
            return True
        except Exception as e:
            print(f"[StorageService] Ошибка удаления: {e}")
            return False

    def file_size(self) -> int:
        """Размер файла в байтах."""
        if not os.path.exists(self._filepath):
            return 0
        return os.path.getsize(self._filepath)

    def __repr__(self):
        return f"<StorageService(filepath={self._filepath!r})>"

    def __str__(self):
        size = self.file_size()
        return f"Хранилище: {self._filepath} ({size} байт)"
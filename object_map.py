"""Пользовательская коллекция-отображение для связки ключ → значение.

Внутри использует список пар, а не встроенный dict. JSON-словарь применяется
только на границе сериализации, поскольку этого требует формат JSON.
"""
from collections.abc import MutableMapping


class ObjectMap(MutableMapping):
    def __init__(self, values=()):
        self._pairs = []
        source = values.items() if hasattr(values, "items") else values
        for key, value in source:
            self[key] = value

    def __getitem__(self, key):
        for stored_key, value in self._pairs:
            if stored_key == key:
                return value
        raise KeyError(key)

    def __setitem__(self, key, value):
        for index, (stored_key, _) in enumerate(self._pairs):
            if stored_key == key:
                self._pairs[index] = (key, value)
                return
        self._pairs.append((key, value))

    def __delitem__(self, key):
        for index, (stored_key, _) in enumerate(self._pairs):
            if stored_key == key:
                del self._pairs[index]
                return
        raise KeyError(key)

    def __iter__(self):
        return (key for key, _ in self._pairs)

    def __len__(self):
        return len(self._pairs)

    def __repr__(self):
        return f"ObjectMap({self._pairs!r})"

    def __str__(self):
        return ", ".join(f"{key}: {value}" for key, value in self._pairs)

    def __eq__(self, other):
        if not hasattr(other, "items"):
            return NotImplemented
        return all(key in other and other[key] == value for key, value in self._pairs) and len(self) == len(other)

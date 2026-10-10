# Карта соответствия требованиям ТЗ

## 1. Сущности описаны классами

**Требование ТЗ:** «Все сущности должны быть описаны через классы».

**Где смотреть:**

- `entities/abstract_entity.py` — базовый класс `AbstractEntity`.
- `entities/car.py` — `Car`.
- `entities/customer.py` — `Customer`.
- `entities/rental.py` — `Rental`.
- `entities/payment.py` — `Payment`.
- `entities/employee.py` — `Employee`.
- `entities/category.py` — `Category`.
- `entities/location.py` — `Location`.
- `entities/insurance.py` — `Insurance`.
- `entities/maintenance.py` — `Maintenance`.
- `entities/damage_report.py` — `DamageReport`.
- `services/report_service.py` — `WorkSession` 

## 2. Переопределить не менее 10 компонентов окна

**Требование ТЗ:** «Переопределить как минимум 10 любых компонента окна».

1. `ui/components/header_bar.py` — `HeaderBar(QFrame)`.
2. `ui/components/confirm_dialog.py` — `ConfirmDialog(QDialog)`.
3. `ui/components/car_tile.py` — `CarTile(QFrame)`.
4. `ui/components/custom_line_edit.py` — `CustomLineEdit(QLineEdit)`.
5. `ui/components/rental_card.py` — `RentalCard(QFrame)`.
6. `ui/components/money_label.py` — `MoneyLabel(QLabel)`.
7. `ui/components/status_badge.py` — `StatusBadge(QLabel)`.
8. `ui/components/stat_card.py` — `StatCard(QFrame)`.
9. `ui/components/customer_card.py` — `CustomerCard(QFrame)`.
10. `ui/components/search_field.py` — `SearchField(QFrame)`.
11. `ui/dialogs/add_customer_dialog.py` — `AddCustomerDialog(QDialog)`.
12. `ui/dialogs/add_car_dialog.py` — `AddCarDialog(QDialog)`.
13. `ui/dialogs/add_rental_dialog.py` — `AddRentalDialog(QDialog)`.
14. `ui/main_window.py` — `MetricCard(QFrame)`, `RevenueChart(QWidget)`, `RentalDialog(QDialog)`, `ReturnDialog(QDialog)`, `MainWindow(QMainWindow)`.

В этих классах задаются собственная структура, поведение и оформление Qt-виджетов. Размещение выполняется через Qt Layouts.

## 3. Функциональность реализована методами классов или объектов

**Требование ТЗ:** функциональность должна быть реализована через методы класса (`@staticmethod`) или объекта.

- `entities/*.py` — валидация, свойства и методы сущностей.
- `services/storage_service.py` — `StorageService.load_all()`, `StorageService.save_all()`.
- `services/report_service.py` — `ReportService.start_session()`, `finish_session()`, `generate_report()`, `save_to_file()`.
- `services/rental_workflow.py` — операции бизнес-процесса аренды.
- `ui/main_window.py` — обработчики действий интерфейса, включая `closeEvent()`.
- `object_map.py` — методы пользовательского отображения `ObjectMap`.

## 4. Сущности наследуются от абстрактного класса

**Требование ТЗ:** пользовательские сущности должны наследоваться от абстрактного класса.

`entities/abstract_entity.py`.

`AbstractEntity` наследуется от `ABC` и объявляет абстрактные методы `validate()`, `to_dict()` и `from_dict()`. Бизнес-сущности, например `Car`, `Customer`, `Rental` и `Payment`, наследуются от `AbstractEntity`.

поискать в `class ... (AbstractEntity)` и в каталоге `entities/`.

## 5. Специальные методы, включая `__eq__`, `__repr__`, `__str__`

**Требование ТЗ:** пользовательские классы должны переопределять специальные методы, включая эти три.

**Где смотреть:**

- `entities/abstract_entity.py` — базовые реализации `__eq__()`, `__hash__()`, `__repr__()`, `__str__()`, `__lt__()`.
- `entities/car.py`, `customer.py`, `rental.py`, `payment.py`, `employee.py`, `category.py`, `location.py`, `insurance.py`, `maintenance.py`, `damage_report.py` — переопределения методов сущностей.
- `services/report_service.py` — `WorkSession` реализует `__eq__()`, `__lt__()`, `__hash__()`, `__repr__()`, `__str__()`; `ReportService` также имеет специальные методы.
- `ui/components/*.py` — некоторые пользовательские виджеты также реализуют специальные методы.

## 6. Пользовательские классы должны быть сравнимы

**Требование ТЗ:** пользовательские классы должны быть сравнимы.

- `entities/abstract_entity.py` — сравнение по идентификатору через `__eq__()` и упорядочивание через `__lt__()`.
- Файлы сущностей в `entities/` — специализированные реализации `__eq__()`.
- `services/report_service.py` — `WorkSession.__eq__()` и `WorkSession.__lt__()`.

**Автоматическая проверка:** `tests_compliance.py`, тест `test_work_session_special_methods_and_round_trip` сравнивает исходную и восстановленную сессию.

## 7. Геттеры и сеттеры атрибутов

**Требование ТЗ:** атрибуты пользовательских классов должны иметь геттеры и сеттеры.

**Где смотреть:**

- `entities/abstract_entity.py` — свойства `id`, `created_at`, `updated_at` и их сеттеры.
- `entities/car.py`, `customer.py`, `rental.py`, `payment.py`, `employee.py`, `category.py`, `location.py`, `insurance.py`, `maintenance.py`, `damage_report.py` — свойства с `@property` и соответствующими `@<property>.setter`.
- `services/report_service.py` — свойства `WorkSession.login`, `time_in`, `time_out` и `ReportService.report_path`.


## 8. Запрет на встроенный `dict` для маппинга

**Требование ТЗ:** «Запрещено использовать Map (dict) — для маппинга используйте свой кастомный класс».

- `object_map.py` — пользовательский класс `ObjectMap`, реализующий `MutableMapping`; пары хранятся во внутреннем списке `_pairs`.
- `entity_storage/entity_collection.py` — пользовательская коллекция сущностей.
- `services/storage_service.py` — для внутренних отображений используется `ObjectMap`.
- `entities/*.py` — `to_dict()` возвращает `ObjectMap`.

**Граница формата JSON:** `services/storage_service.py` преобразует сущности в JSON-совместимые значения и использует `json.dump()` / `json.load()`. Встроенные словари могут появляться на границе сериализации/десериализации, так как JSON-объекты представлены словарями в Python. В бизнес-коллекциях отображение реализовано через `ObjectMap`.

**Автоматическая проверка:** `tests_compliance.py`, тест `test_custom_mapping` проверяет чтение, запись и количество пар `ObjectMap`.

## 9. Использовать не менее пяти UI-компонентов

**Требование ТЗ:** использовать не менее пяти UI-компонентов.

**Cмотреть:** `ui/main_window.py`, `ui/components/` и `ui/dialogs/`.

Примеры: `QMainWindow`, `QWidget`, `QLabel`, `QPushButton`, `QLineEdit`, `QTableWidget`, `QComboBox`, `QDateEdit`, `QSpinBox`, `QDialog`.

## 10. Не менее десяти пользовательских объектов

**Требование ТЗ:** создать не менее десяти пользовательских объектов; их можно хранить в `list`, `tuple`, `set`.

- `data.json` — демонстрационные данные приложения.
- `services/storage_service.py` — загрузка данных и построение коллекций сущностей.
- `entity_storage/entity_collection.py` — хранение коллекций объектов.
- `entities/*.py` — классы, экземпляры которых создаются при загрузке данных.


## 11. Все компоненты должны быть выровнены

**Требование ТЗ:** все компоненты интерфейса должны быть выровнены.

- `ui/main_window.py` — основные экраны и компоновки.
- `ui/components/*.py` — компоновки отдельных виджетов.
- `ui/dialogs/*.py` — компоновки диалоговых окон.

В проекте используются `QVBoxLayout`, `QHBoxLayout`, `QFormLayout` и другие Qt Layouts, которые помогают сохранять выравнивание при изменении размера окна.


## 12. При закрытии приложения сохраняется отчёт о рабочей сессии

**Требование ТЗ:** при закрытии приложения сохраняется файл отчёта с колонками `login`, `time_in`, `time_out`.

- `main.py` — создание `ReportService("report.txt")` и передача его в `MainWindow`.
- `ui/main_window.py`, `MainWindow.__init__()` — запуск сессии через `start_session()`.
- `ui/main_window.py`, `MainWindow.closeEvent()` — фиксация времени выхода и сохранение отчёта при подтверждённом закрытии.
- `services/report_service.py`, `WorkSession` — модель рабочей сессии.
- `services/report_service.py`, `ReportService.generate_report()` — формирование таблицы.
- `services/report_service.py`, `ReportService.save_to_file()` — запись `report.txt`.


**Формат времени:** `%d.%m.%Y %H:%M:%S`, задан в `ReportService.TIME_FORMAT`.

**Автоматическая проверка:** `tests_compliance.py`, тест `test_report_format_and_history` проверяет названия колонок, формат времени и чтение истории.

## 13. Формат и совместимость данных

- `data.json` — исходный файл данных.
- `services/storage_service.py` — `load_all()` и `save_all()`.
- `tests_compliance.py`, `test_json_compatibility_round_trip` — проверка сохранения и повторной загрузки коллекций без изменения количества сущностей.

## 14. Запуск проверок

Из каталога `car_rental/` выполнить:

```bash
python -m unittest tests_compliance.py -v
python -m compileall -q .
python main.py
```

Для запуска интерфейса нужно установи зависимости:

```bash
python -m pip install -r requirements.txt
```

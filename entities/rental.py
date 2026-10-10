from entities.abstract_entity import AbstractEntity
from datetime import datetime, date
from functools import total_ordering


from object_map import ObjectMap
class RentalStatus:
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


@total_ordering
class Rental(AbstractEntity):
    """Аренда автомобиля."""

    def __init__(self, customer_id: str, customer_name: str,
                 car_id: str, car_info: str,
                 employee_id: str, employee_login: str,
                 start_date: datetime, end_date: datetime,
                 days: int, total_cost: float,
                 status: str = RentalStatus.ACTIVE,
                 actual_return: datetime = None,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.car_id = car_id
        self.car_info = car_info
        self.employee_id = employee_id
        self.employee_login = employee_login
        self.start_date = start_date
        self.end_date = end_date
        self.days = days
        self.total_cost = total_cost
        self.status = status
        self.actual_return = actual_return

    # --- Геттеры ---
    @property
    def customer_id(self) -> str: return self._customer_id
    @property
    def customer_name(self) -> str: return self._customer_name
    @property
    def car_id(self) -> str: return self._car_id
    @property
    def car_info(self) -> str: return self._car_info
    @property
    def employee_id(self) -> str: return self._employee_id
    @property
    def employee_login(self) -> str: return self._employee_login
    @property
    def start_date(self) -> datetime: return self._start_date
    @property
    def end_date(self) -> datetime: return self._end_date
    @property
    def days(self) -> int: return self._days
    @property
    def total_cost(self) -> float: return self._total_cost
    @property
    def status(self) -> str: return self._status
    @property
    def actual_return(self) -> datetime: return self._actual_return

    # --- Сеттеры (с валидацией) ---
    @customer_id.setter
    def customer_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("customer_id обязателен")
        self._customer_id = value
        self.updated_at = datetime.now()

    @customer_name.setter
    def customer_name(self, value: str):
        if not isinstance(value, str) or len(value.strip()) < 5:
            raise ValueError("Имя клиента >= 5 символов")
        self._customer_name = value.strip().title()
        self.updated_at = datetime.now()

    @car_id.setter
    def car_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("car_id обязателен")
        self._car_id = value
        self.updated_at = datetime.now()

    @car_info.setter
    def car_info(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("car_info обязателен")
        self._car_info = value.strip()
        self.updated_at = datetime.now()

    @employee_id.setter
    def employee_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("employee_id обязателен")
        self._employee_id = value
        self.updated_at = datetime.now()

    @employee_login.setter
    def employee_login(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("employee_login обязателен")
        self._employee_login = value.strip()
        self.updated_at = datetime.now()

    @start_date.setter
    def start_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("start_date должен быть datetime")
        self._start_date = value
        self.updated_at = datetime.now()

    @end_date.setter
    def end_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("end_date должен быть datetime")
        if value <= self._start_date:
            raise ValueError("end_date должен быть позже start_date")
        self._end_date = value
        self.updated_at = datetime.now()

    @days.setter
    def days(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("days > 0")
        self._days = value
        self.updated_at = datetime.now()

    @total_cost.setter
    def total_cost(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("total_cost >= 0")
        self._total_cost = float(value)
        self.updated_at = datetime.now()

    @status.setter
    def status(self, value: str):
        allowed = {RentalStatus.ACTIVE, RentalStatus.COMPLETED,
                   RentalStatus.CANCELLED, RentalStatus.OVERDUE}
        if value not in allowed:
            raise ValueError(f"Статус: {allowed}")
        self._status = value
        self.updated_at = datetime.now()

    @actual_return.setter
    def actual_return(self, value: datetime):
        if value is not None and not isinstance(value, datetime):
            raise TypeError("actual_return должен быть datetime или None")
        self._actual_return = value
        self.updated_at = datetime.now()

    # --- Бизнес-методы ---
    @staticmethod
    def calculate_days(start: datetime, end: datetime) -> int:
        delta = end - start
        return max(1, delta.days + (1 if delta.seconds > 0 else 0))

    def complete(self, return_date: datetime = None):
        self.actual_return = return_date or datetime.now()
        self.status = RentalStatus.COMPLETED

    def cancel(self):
        self.status = RentalStatus.CANCELLED

    def mark_overdue(self):
        self.status = RentalStatus.OVERDUE

    def is_overdue(self) -> bool:
        return (self._status == RentalStatus.ACTIVE and
                datetime.now() > self._end_date)

    def validate(self) -> bool:
        return all([
            bool(self._customer_id),
            bool(self._car_id),
            bool(self._employee_id),
            self._start_date < self._end_date,
            self._days > 0,
            self._total_cost >= 0,
            self._status in {RentalStatus.ACTIVE, RentalStatus.COMPLETED,
                             RentalStatus.CANCELLED, RentalStatus.OVERDUE},
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Rental'), ('id', self._id), ('customer_id', self._customer_id), ('customer_name', self._customer_name), ('car_id', self._car_id), ('car_info', self._car_info), ('employee_id', self._employee_id), ('employee_login', self._employee_login), ('start_date', self._start_date.isoformat()), ('end_date', self._end_date.isoformat()), ('days', self._days), ('total_cost', self._total_cost), ('status', self._status), ('actual_return', self._actual_return.isoformat() if self._actual_return else None), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Rental':
        return cls(
            customer_id=data['customer_id'], customer_name=data['customer_name'],
            car_id=data['car_id'], car_info=data['car_info'],
            employee_id=data['employee_id'], employee_login=data['employee_login'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            days=data['days'], total_cost=data['total_cost'],
            status=data.get('status', RentalStatus.ACTIVE),
            actual_return=datetime.fromisoformat(data['actual_return']) if data.get('actual_return') else None,
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    # --- Спец. методы ---
    def __eq__(self, other):
        if isinstance(other, Rental):
            return self._id == other._id
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Rental):
            return self._start_date < other._start_date
        return NotImplemented

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<Rental(id={self._id[:8]}, customer={self._customer_name!r}, status={self._status})>"

    def __str__(self):
        return f"{self._customer_name} → {self._car_info} ({self._days} дн., {self._total_cost} ₽)"

    def __sub__(self, other):
        """Разница между двумя арендами в днях."""
        if isinstance(other, Rental):
            return (self._start_date - other._start_date).days
        return NotImplemented
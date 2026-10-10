from entities.abstract_entity import AbstractEntity
from datetime import datetime, date
from functools import total_ordering


from object_map import ObjectMap
class MaintenanceType:
    OIL_CHANGE = "oil_change"
    TIRE_CHANGE = "tire_change"
    DIAGNOSTICS = "diagnostics"
    REPAIR = "repair"
    FULL_SERVICE = "full_service"


@total_ordering
class Maintenance(AbstractEntity):
    """ТО автомобиля."""

    def __init__(self, car_id: str, maintenance_type: str,
                 maintenance_date: date, mileage_at_service: int,
                 cost: float, description: str = "",
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.car_id = car_id
        self.maintenance_type = maintenance_type
        self.maintenance_date = maintenance_date
        self.mileage_at_service = mileage_at_service
        self.cost = cost
        self.description = description

    @property
    def car_id(self) -> str: return self._car_id
    @property
    def maintenance_type(self) -> str: return self._maintenance_type
    @property
    def maintenance_date(self) -> date: return self._maintenance_date
    @property
    def mileage_at_service(self) -> int: return self._mileage_at_service
    @property
    def cost(self) -> float: return self._cost
    @property
    def description(self) -> str: return self._description

    @car_id.setter
    def car_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("car_id обязателен")
        self._car_id = value
        self.updated_at = datetime.now()

    @maintenance_type.setter
    def maintenance_type(self, value: str):
        allowed = {MaintenanceType.OIL_CHANGE, MaintenanceType.TIRE_CHANGE,
                   MaintenanceType.DIAGNOSTICS, MaintenanceType.REPAIR,
                   MaintenanceType.FULL_SERVICE}
        if value not in allowed:
            raise ValueError(f"Тип: {allowed}")
        self._maintenance_type = value
        self.updated_at = datetime.now()

    @maintenance_date.setter
    def maintenance_date(self, value: date):
        if not isinstance(value, date):
            raise TypeError("maintenance_date должен быть datetime.date")
        if value > date.today():
            raise ValueError("Дата ТО не может быть в будущем")
        self._maintenance_date = value
        self.updated_at = datetime.now()

    @mileage_at_service.setter
    def mileage_at_service(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Пробег >= 0")
        self._mileage_at_service = value
        self.updated_at = datetime.now()

    @cost.setter
    def cost(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Стоимость >= 0")
        self._cost = float(value)
        self.updated_at = datetime.now()

    @description.setter
    def description(self, value: str):
        if not isinstance(value, str):
            raise TypeError("description должен быть str")
        self._description = value.strip()
        self.updated_at = datetime.now()

    def validate(self) -> bool:
        return all([
            bool(self._car_id),
            self._maintenance_type in {MaintenanceType.OIL_CHANGE, MaintenanceType.TIRE_CHANGE,
                                       MaintenanceType.DIAGNOSTICS, MaintenanceType.REPAIR,
                                       MaintenanceType.FULL_SERVICE},
            self._maintenance_date <= date.today(),
            self._mileage_at_service >= 0,
            self._cost >= 0,
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Maintenance'), ('id', self._id), ('car_id', self._car_id), ('maintenance_type', self._maintenance_type), ('maintenance_date', self._maintenance_date.isoformat()), ('mileage_at_service', self._mileage_at_service), ('cost', self._cost), ('description', self._description), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Maintenance':
        return cls(
            car_id=data['car_id'], maintenance_type=data['maintenance_type'],
            maintenance_date=date.fromisoformat(data['maintenance_date']),
            mileage_at_service=data['mileage_at_service'],
            cost=data['cost'], description=data.get('description', ''),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    def __eq__(self, other):
        if isinstance(other, Maintenance):
            return self._id == other._id
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Maintenance):
            return self._maintenance_date < other._maintenance_date
        return NotImplemented

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<Maintenance(type={self._maintenance_type!r}, cost={self._cost})>"

    def __str__(self):
        return f"ТО {self._maintenance_type} ({self._maintenance_date}) — {self._cost} ₽"

    def __add__(self, other):
        """Сумма двух ТО."""
        if isinstance(other, Maintenance):
            return self._cost + other._cost
        return NotImplemented
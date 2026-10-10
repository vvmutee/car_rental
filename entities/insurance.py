from entities.abstract_entity import AbstractEntity
from datetime import datetime, date
from functools import total_ordering


from object_map import ObjectMap
class InsuranceType:
    OSAGO = "osago"
    KASKO = "kasko"
    FULL = "full"


@total_ordering
class Insurance(AbstractEntity):
    """Страховка к аренде."""

    def __init__(self, insurance_type: str, cost: float, coverage: float,
                 valid_from: date, valid_to: date,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.insurance_type = insurance_type
        self.cost = cost
        self.coverage = coverage
        self.valid_from = valid_from
        self.valid_to = valid_to

    @property
    def insurance_type(self) -> str: return self._insurance_type
    @property
    def cost(self) -> float: return self._cost
    @property
    def coverage(self) -> float: return self._coverage
    @property
    def valid_from(self) -> date: return self._valid_from
    @property
    def valid_to(self) -> date: return self._valid_to

    @insurance_type.setter
    def insurance_type(self, value: str):
        allowed = {InsuranceType.OSAGO, InsuranceType.KASKO, InsuranceType.FULL}
        if value not in allowed:
            raise ValueError(f"Тип: {allowed}")
        self._insurance_type = value
        self.updated_at = datetime.now()

    @cost.setter
    def cost(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Стоимость >= 0")
        self._cost = float(value)
        self.updated_at = datetime.now()

    @coverage.setter
    def coverage(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Покрытие > 0")
        self._coverage = float(value)
        self.updated_at = datetime.now()

    @valid_from.setter
    def valid_from(self, value: date):
        if not isinstance(value, date):
            raise TypeError("valid_from должен быть datetime.date")
        self._valid_from = value
        self.updated_at = datetime.now()

    @valid_to.setter
    def valid_to(self, value: date):
        if not isinstance(value, date):
            raise TypeError("valid_to должен быть datetime.date")
        if value <= self._valid_from:
            raise ValueError("valid_to должен быть позже valid_from")
        self._valid_to = value
        self.updated_at = datetime.now()

    def is_active_on(self, check_date: date) -> bool:
        return self._valid_from <= check_date <= self._valid_to

    def validate(self) -> bool:
        return all([
            self._insurance_type in {InsuranceType.OSAGO, InsuranceType.KASKO, InsuranceType.FULL},
            self._cost >= 0,
            self._coverage > 0,
            self._valid_from < self._valid_to,
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Insurance'), ('id', self._id), ('insurance_type', self._insurance_type), ('cost', self._cost), ('coverage', self._coverage), ('valid_from', self._valid_from.isoformat()), ('valid_to', self._valid_to.isoformat()), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Insurance':
        return cls(
            insurance_type=data['insurance_type'],
            cost=data['cost'], coverage=data['coverage'],
            valid_from=date.fromisoformat(data['valid_from']),
            valid_to=date.fromisoformat(data['valid_to']),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    def __eq__(self, other):
        if isinstance(other, Insurance):
            return self._id == other._id
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Insurance):
            return self._cost < other._cost
        return NotImplemented

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<Insurance(type={self._insurance_type!r}, cost={self._cost})>"

    def __str__(self):
        return f"{self._insurance_type.upper()} — {self._cost} ₽ (покрытие {self._coverage} ₽)"

    def __add__(self, other):
        """Сложение двух страховок = суммарная стоимость."""
        if isinstance(other, Insurance):
            return self._cost + other._cost
        return NotImplemented
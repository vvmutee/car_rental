from entities.abstract_entity import AbstractEntity
from datetime import datetime
from functools import total_ordering


from object_map import ObjectMap
@total_ordering
class DamageReport(AbstractEntity):
    """Акт повреждений при возврате авто."""

    def __init__(self, rental_id: str, description: str, damage_amount: float,
                 report_date: datetime = None,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.rental_id = rental_id
        self.description = description
        self.damage_amount = damage_amount
        self.report_date = report_date or datetime.now()

    @property
    def rental_id(self) -> str: return self._rental_id
    @property
    def description(self) -> str: return self._description
    @property
    def damage_amount(self) -> float: return self._damage_amount
    @property
    def report_date(self) -> datetime: return self._report_date

    @rental_id.setter
    def rental_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("rental_id обязателен")
        self._rental_id = value
        self.updated_at = datetime.now()

    @description.setter
    def description(self, value: str):
        if not isinstance(value, str) or len(value.strip()) < 3:
            raise ValueError("Описание >= 3 символов")
        self._description = value.strip()
        self.updated_at = datetime.now()

    @damage_amount.setter
    def damage_amount(self, value: float):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Сумма ущерба >= 0")
        self._damage_amount = float(value)
        self.updated_at = datetime.now()

    @report_date.setter
    def report_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("report_date должен быть datetime")
        self._report_date = value
        self.updated_at = datetime.now()

    def validate(self) -> bool:
        return all([
            bool(self._rental_id),
            len(self._description) >= 3,
            self._damage_amount >= 0,
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'DamageReport'), ('id', self._id), ('rental_id', self._rental_id), ('description', self._description), ('damage_amount', self._damage_amount), ('report_date', self._report_date.isoformat()), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'DamageReport':
        return cls(
            rental_id=data['rental_id'], description=data['description'],
            damage_amount=data['damage_amount'],
            report_date=datetime.fromisoformat(data['report_date']),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    def __eq__(self, other):
        if isinstance(other, DamageReport):
            return self._id == other._id
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, DamageReport):
            return self._damage_amount < other._damage_amount
        return NotImplemented

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<DamageReport(amount={self._damage_amount})>"

    def __str__(self):
        return f"Акт #{self._id[:8]}: ущерб {self._damage_amount} ₽"

    def __add__(self, other):
        """Сумма двух актов повреждений."""
        if isinstance(other, DamageReport):
            return self._damage_amount + other._damage_amount
        return NotImplemented
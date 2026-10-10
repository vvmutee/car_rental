from entities.abstract_entity import AbstractEntity
from datetime import datetime
from functools import total_ordering


from object_map import ObjectMap
class PaymentMethod:
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"


class PaymentStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"


@total_ordering
class Payment(AbstractEntity):
    """Платеж по аренде."""

    def __init__(self, rental_id: str, amount: float, method: str,
                 payment_date: datetime = None, status: str = PaymentStatus.PENDING,
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.rental_id = rental_id
        self.amount = amount
        self.method = method
        self.payment_date = payment_date or datetime.now()
        self.status = status

    @property
    def rental_id(self) -> str: return self._rental_id
    @property
    def amount(self) -> float: return self._amount
    @property
    def method(self) -> str: return self._method
    @property
    def payment_date(self) -> datetime: return self._payment_date
    @property
    def status(self) -> str: return self._status

    @rental_id.setter
    def rental_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("rental_id обязателен")
        self._rental_id = value
        self.updated_at = datetime.now()

    @amount.setter
    def amount(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Сумма > 0")
        self._amount = float(value)
        self.updated_at = datetime.now()

    @method.setter
    def method(self, value: str):
        allowed = {PaymentMethod.CASH, PaymentMethod.CARD, PaymentMethod.TRANSFER}
        if value not in allowed:
            raise ValueError(f"Способ: {allowed}")
        self._method = value
        self.updated_at = datetime.now()

    @payment_date.setter
    def payment_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("payment_date должен быть datetime")
        self._payment_date = value
        self.updated_at = datetime.now()

    @status.setter
    def status(self, value: str):
        allowed = {PaymentStatus.PENDING, PaymentStatus.COMPLETED, PaymentStatus.REFUNDED}
        if value not in allowed:
            raise ValueError(f"Статус: {allowed}")
        self._status = value
        self.updated_at = datetime.now()

    def complete(self):
        self.status = PaymentStatus.COMPLETED

    def refund(self):
        self.status = PaymentStatus.REFUNDED

    def validate(self) -> bool:
        return all([
            bool(self._rental_id),
            self._amount > 0,
            self._method in {PaymentMethod.CASH, PaymentMethod.CARD, PaymentMethod.TRANSFER},
            self._status in {PaymentStatus.PENDING, PaymentStatus.COMPLETED, PaymentStatus.REFUNDED},
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Payment'), ('id', self._id), ('rental_id', self._rental_id), ('amount', self._amount), ('method', self._method), ('payment_date', self._payment_date.isoformat()), ('status', self._status), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Payment':
        return cls(
            rental_id=data['rental_id'], amount=data['amount'],
            method=data['method'],
            payment_date=datetime.fromisoformat(data['payment_date']),
            status=data.get('status', PaymentStatus.PENDING),
            entity_id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
        )

    def __eq__(self, other):
        if isinstance(other, Payment):
            return self._id == other._id
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Payment):
            return self._amount < other._amount
        return NotImplemented

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<Payment(amount={self._amount}, method={self._method})>"

    def __str__(self):
        return f"{self._amount} ₽ ({self._method}) — {self._status}"

    def __add__(self, other):
        """Сумма двух платежей."""
        if isinstance(other, Payment):
            return self._amount + other._amount
        if isinstance(other, (int, float)):
            return self._amount + other
        return NotImplemented
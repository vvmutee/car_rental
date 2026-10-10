from entities.abstract_entity import AbstractEntity
from datetime import datetime, date
from functools import total_ordering
import hashlib
import re


from object_map import ObjectMap
@total_ordering
class Employee(AbstractEntity):
    """Сотрудник проката."""

    def __init__(self, full_name: str, position: str, login: str, password: str,
                 hire_date: date, phone: str = "",
                 entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.full_name = full_name
        self.position = position
        self.login = login
        self.password = password
        self.hire_date = hire_date
        self.phone = phone

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def position(self) -> str:
        return self._position

    @property
    def login(self) -> str:
        return self._login

    @property
    def password(self) -> str:
        return self._password_hash

    @property
    def hire_date(self) -> date:
        return self._hire_date

    @property
    def phone(self) -> str:
        return self._phone

    @full_name.setter
    def full_name(self, value: str):
        if not isinstance(value, str) or len(value.strip()) < 5:
            raise ValueError("ФИО >= 5 символов")
        self._full_name = value.strip().title()
        self.updated_at = datetime.now()

    @position.setter
    def position(self, value: str):
        allowed = {"manager", "mechanic", "admin", "cashier"}
        if value.lower() not in allowed:
            raise ValueError(f"Должность: {allowed}")
        self._position = value.lower()
        self.updated_at = datetime.now()

    @login.setter
    def login(self, value: str):
        value = value.strip().lower()
        if not re.match(r'^[a-z0-9_]{3,20}$', value):
            raise ValueError("Логин: 3-20 символов (a-z, 0-9, _)")
        self._login = value
        self.updated_at = datetime.now()

    @password.setter
    def password(self, value: str):
        if not isinstance(value, str) or len(value) < 6:
            raise ValueError("Пароль >= 6 символов")
        self._password_hash = hashlib.sha256(value.encode()).hexdigest()
        self.updated_at = datetime.now()

    @hire_date.setter
    def hire_date(self, value: date):
        if not isinstance(value, date):
            raise TypeError("hire_date должен быть datetime.date")
        if value > date.today():
            raise ValueError("Дата найма не может быть в будущем")
        self._hire_date = value
        self.updated_at = datetime.now()

    @phone.setter
    def phone(self, value: str):
        digits = re.sub(r'\D', '', value)
        if value and len(digits) != 11:
            raise ValueError("Телефон: 11 цифр")
        self._phone = f"+{digits}" if digits else ""
        self.updated_at = datetime.now()

    def check_password(self, password: str) -> bool:
        return self._password_hash == hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def validate(self) -> bool:
        return all([
            len(self._full_name) >= 5,
            self._position in {"manager", "mechanic", "admin", "cashier"},
            re.match(r'^[a-z0-9_]{3,20}$', self._login),
            bool(self._password_hash),
            self._hire_date <= date.today(),
        ])

    def to_dict(self) -> ObjectMap:
        return ObjectMap([('type', 'Employee'), ('id', self._id), ('full_name', self._full_name), ('position', self._position), ('login', self._login), ('password_hash', self._password_hash), ('hire_date', self._hire_date.isoformat()), ('phone', self._phone), ('created_at', self._created_at.isoformat()), ('updated_at', self._updated_at.isoformat())])

    @classmethod
    def from_dict(cls, data) -> 'Employee':
        emp = cls.__new__(cls)
        AbstractEntity.__init__(emp, data['id'], datetime.fromisoformat(data['created_at']))
        emp._full_name = data['full_name']
        emp._position = data['position']
        emp._login = data['login']
        emp._password_hash = data['password_hash']
        emp._hire_date = date.fromisoformat(data['hire_date'])
        emp._phone = data.get('phone', '')
        emp.updated_at = datetime.fromisoformat(data['updated_at'])
        return emp

    def __eq__(self, other):
        if isinstance(other, Employee):
            return self._login == other._login
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Employee):
            return self._full_name < other._full_name
        return NotImplemented

    def __hash__(self):
        return hash(self._login)

    def __repr__(self):
        return f"<Employee(login={self._login!r}, position={self._position})>"

    def __str__(self):
        return f"{self._full_name} ({self._login})"
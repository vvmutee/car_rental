"""Отчёт о рабочих сессиях приложения в формате, заданном ТЗ."""
from datetime import datetime
import os
import re
from typing import List
from collections.abc import Mapping
from entities.abstract_entity import AbstractEntity
from object_map import ObjectMap


class WorkSession(AbstractEntity):
    """Одна сессия работы приложения: логин, вход и выход."""
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, login: str, time_in: datetime, time_out: datetime = None, entity_id: str = None, created_at: datetime = None):
        super().__init__(entity_id, created_at)
        self.login = login
        self.time_in = time_in
        self.time_out = time_out or time_in

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("login не может быть пустым")
        self._login = value.strip()

    @property
    def time_in(self) -> datetime:
        return self._time_in

    @time_in.setter
    def time_in(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError("time_in должен быть datetime")
        self._time_in = value
        if hasattr(self, "_time_out") and self._time_out < value:
            self._time_out = value

    @property
    def time_out(self) -> datetime:
        return self._time_out

    @time_out.setter
    def time_out(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError("time_out должен быть datetime")
        if value < self._time_in:
            raise ValueError("time_out не может быть раньше time_in")
        self._time_out = value

    def validate(self) -> bool:
        return bool(self.login.strip()) and isinstance(self.time_in, datetime) and isinstance(self.time_out, datetime) and self.time_out >= self.time_in

    def to_dict(self):
        return ObjectMap([("type", "WorkSession"), ("id", self.id), ("login", self.login), ("time_in", self.time_in.isoformat()), ("time_out", self.time_out.isoformat()), ("created_at", self.created_at.isoformat())])

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, Mapping):
            raise TypeError("data должен поддерживать отображение ключей")
        return cls(data["login"], datetime.fromisoformat(data["time_in"]),
                   datetime.fromisoformat(data["time_out"]), data.get("id"),
                   datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None)

    def __eq__(self, other):
        if not isinstance(other, WorkSession):
            return NotImplemented
        return (self.login, self.time_in, self.time_out) == (other.login, other.time_in, other.time_out)

    def __lt__(self, other):
        if not isinstance(other, WorkSession):
            return NotImplemented
        return self.time_in < other.time_in

    def __hash__(self):
        return hash((self.login, self.time_in, self.time_out))

    def __repr__(self):
        return f"WorkSession(login={self.login!r}, time_in={self.time_in!r}, time_out={self.time_out!r})"

    def __str__(self):
        return f"{self.login}: {self.time_in.strftime(self.TIME_FORMAT)} — {self.time_out.strftime(self.TIME_FORMAT)}"


class ReportService:
    """Формирует ASCII-таблицу строго с полями login, time_in, time_out."""
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
    _ROW_PATTERN = re.compile(r"^\|\s*(.*?)\s*\|\s*(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})\s*\|\s*(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})\s*\|$")

    def __init__(self, report_path: str = "report.txt"):
        self._report_path = report_path
        self._sessions: List[WorkSession] = []
        self._current_session = None
        self._load_existing_sessions()

    @property
    def report_path(self) -> str:
        return self._report_path

    @report_path.setter
    def report_path(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("report_path не может быть пустым")
        self._report_path = value.strip()

    @property
    def sessions(self) -> List[WorkSession]:
        return list(self._sessions)

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    def start_session(self, login: str, time_in: datetime = None) -> WorkSession:
        """Создаёт запись при старте приложения."""
        if self._current_session is not None:
            self.finish_session()
        now = time_in or datetime.now()
        self._current_session = WorkSession(login, now, now)
        self._sessions.append(self._current_session)
        return self._current_session

    def finish_session(self, time_out: datetime = None) -> None:
        """Фиксирует time_out при закрытии приложения."""
        if self._current_session is not None:
            self._current_session.time_out = time_out or datetime.now()
            self._current_session = None

    def add_session(self, session: WorkSession) -> None:
        if not isinstance(session, WorkSession):
            raise TypeError("Ожидается WorkSession")
        self._sessions.append(session)

    def clear_sessions(self) -> None:
        self._sessions.clear()
        self._current_session = None

    def generate_report(self) -> str:
        headers = ["login", "time_in", "time_out"]
        rows = [[s.login, s.time_in.strftime(self.TIME_FORMAT), s.time_out.strftime(self.TIME_FORMAT)]
                for s in sorted(self._sessions)]
        widths = [len(x) for x in headers]
        for row in rows:
            for i, value in enumerate(row):
                widths[i] = max(widths[i], len(value))
        separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
        def format_row(values):
            return "|" + "|".join(f" {value:<{widths[i]}} " for i, value in enumerate(values)) + "|"
        lines = [separator, format_row(headers), separator]
        lines.extend(format_row(row) for row in rows)
        lines.append(separator)
        return "\n".join(lines)

    def save_to_file(self) -> bool:
        try:
            folder = os.path.dirname(os.path.abspath(self._report_path))
            os.makedirs(folder, exist_ok=True)
            with open(self._report_path, "w", encoding="utf-8") as stream:
                stream.write(self.generate_report() + "\n")
            return True
        except OSError as exc:
            print(f"[ReportService] Ошибка сохранения отчёта: {exc}")
            return False

    def _load_existing_sessions(self) -> None:
        """Сохраняет историю запусков между перезапусками, если файл уже есть."""
        if not os.path.exists(self._report_path):
            return
        try:
            with open(self._report_path, "r", encoding="utf-8") as stream:
                for line in stream:
                    match = self._ROW_PATTERN.match(line.rstrip("\n"))
                    if match:
                        login, start_text, end_text = match.groups()
                        start = datetime.strptime(start_text, self.TIME_FORMAT)
                        end = datetime.strptime(end_text, self.TIME_FORMAT)
                        self._sessions.append(WorkSession(login, start, end))
        except (OSError, ValueError):
            # Не блокируем запуск приложения из-за старого/повреждённого отчёта.
            self._sessions = []

    def load_from_file(self) -> bool:
        return os.path.exists(self._report_path)

    def get_file_size(self) -> int:
        return os.path.getsize(self._report_path) if os.path.exists(self._report_path) else 0

    def __repr__(self):
        return f"ReportService(path={self._report_path!r}, sessions={self.session_count})"

    def __str__(self):
        return f"Отчёт: {self._report_path} ({self.session_count} сессий)"

    def __len__(self):
        return self.session_count

    def __iter__(self):
        return iter(self._sessions)

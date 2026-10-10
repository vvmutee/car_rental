from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt


class ConfirmDialog(QDialog):
    """
    Диалог подтверждения действия.
    Переопределяет QDialog.
    """

    def __init__(self, title: str, message: str,
                 confirm_text: str = "Подтвердить",
                 cancel_text: str = "Отмена",
                 parent: QWidget = None):
        super().__init__(parent)
        self._title = title
        self._message = message
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._confirmed = False

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        self.setWindowTitle(self._title)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Заголовок
        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #212121;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Сообщение
        msg_label = QLabel(self._message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; color: #424242;")
        msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_label, alignment=Qt.AlignCenter)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignCenter)

        self._cancel_btn = QPushButton(self._cancel_text)
        self._cancel_btn.setMinimumWidth(120)
        self._cancel_btn.setMinimumHeight(36)
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn, alignment=Qt.AlignCenter)

        self._confirm_btn = QPushButton(self._confirm_text)
        self._confirm_btn.setMinimumWidth(120)
        self._confirm_btn.setMinimumHeight(36)
        self._confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self._confirm_btn, alignment=Qt.AlignCenter)

        layout.addLayout(btn_layout)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            QPushButton {
                background: #e0e0e0;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                color: #212121;
            }
            QPushButton:hover {
                background: #bdbdbd;
            }
        """)
        self._confirm_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)

    def _on_confirm(self):
        self._confirmed = True
        self.accept()

    # --- Публичные методы ---
    def is_confirmed(self) -> bool:
        return self._confirmed

    # --- Геттеры/сеттеры ---
    @property
    def title(self) -> str: return self._title
    @title.setter
    def title(self, value: str): self._title = value

    @property
    def message(self) -> str: return self._message
    @message.setter
    def message(self, value: str): self._message = value

    # --- Спец. методы ---
    def __repr__(self):
        return f"<ConfirmDialog(title={self._title!r}, confirmed={self._confirmed})>"

    def __str__(self):
        return f"Диалог: {self._title}"

    def __eq__(self, other):
        if isinstance(other, ConfirmDialog):
            return self._title == other._title
        return NotImplemented

    def __hash__(self):
        return hash(self._title)

    def __bool__(self):
        return self._confirmed
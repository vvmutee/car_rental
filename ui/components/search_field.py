from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton, QWidget
from PyQt5.QtCore import pyqtSignal, Qt


class SearchField(QFrame):
    """
    Поле поиска с иконкой и кнопкой очистки.
    Переопределяет QFrame.
    """

    search_changed = pyqtSignal(str)
    search_submitted = pyqtSignal(str)

    def __init__(self, placeholder: str = "Поиск...", parent: QWidget = None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignVCenter)

        # Иконка поиска
        self._icon_label = QPushButton("🔍")
        self._icon_label.setFlat(True)
        self._icon_label.setFixedSize(32, 32)
        self._icon_label.clicked.connect(self._on_submit)
        layout.addWidget(self._icon_label, alignment=Qt.AlignLeft)

        # Поле ввода
        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText(self._placeholder)
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._line_edit.returnPressed.connect(self._on_submit)
        layout.addWidget(self._line_edit, stretch=1)

        # Кнопка очистки
        self._clear_btn = QPushButton("✕")
        self._clear_btn.setFlat(True)
        self._clear_btn.setFixedSize(32, 32)
        self._clear_btn.clicked.connect(self.clear)
        self._clear_btn.setVisible(False)
        layout.addWidget(self._clear_btn, alignment=Qt.AlignRight)

    def _apply_style(self):
        self.setStyleSheet("""
            SearchField {
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
            }
            SearchField:focus-within {
                border: 2px solid #2196F3;
            }
            QLineEdit {
                border: none;
                font-size: 14px;
            }
            QPushButton {
                border: none;
                font-size: 16px;
                color: #757575;
            }
            QPushButton:hover {
                color: #2196F3;
            }
        """)
        self.setMinimumHeight(40)

    def _on_text_changed(self, text: str):
        self._clear_btn.setVisible(bool(text))
        self.search_changed.emit(text)

    def _on_submit(self):
        self.search_submitted.emit(self._line_edit.text())

    # --- Публичные методы ---
    def text(self) -> str:
        return self._line_edit.text()

    def clear(self):
        self._line_edit.clear()
        self._clear_btn.setVisible(False)

    # --- Геттеры/сеттеры ---
    @property
    def placeholder(self) -> str: return self._placeholder
    @placeholder.setter
    def placeholder(self, value: str):
        self._placeholder = value
        self._line_edit.setPlaceholderText(value)

    # --- Спец. методы ---
    def __repr__(self):
        return f"<SearchField(placeholder={self._placeholder!r})>"

    def __str__(self):
        return f"Поиск: {self._line_edit.text()}"

    def __eq__(self, other):
        if isinstance(other, SearchField):
            return self.text() == other.text()
        return NotImplemented

    def __hash__(self):
        return hash(self.text())

    def __len__(self):
        return len(self.text())
from datetime import datetime, date, timedelta
import calendar

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QDialog, QFormLayout, QComboBox, QDateEdit,
    QDoubleSpinBox, QSpinBox, QLineEdit, QAbstractItemView, QGroupBox,
    QScrollArea, QSizePolicy
)
from entities import (Category, Customer, Car, Employee, Rental, RentalStatus,
                      CarStatus, PaymentMethod, PaymentStatus)
from entity_storage.entity_collection import EntityCollection
from object_map import ObjectMap
from services.storage_service import StorageService
from services.report_service import ReportService, WorkSession
from services.rental_workflow import find_conflicts, return_rental, register_payment, paid_for_rental

NAVY = '#142338'
BLUE = '#356DF3'
BG = '#F4F7FB'
TEXT = '#172B4D'
MUTED = '#718096'
BORDER = '#E2E8F0'
WHITE = '#FFFFFF'


def money(value):
    return f"{value:,.0f} ₽".replace(',', ' ')


def dt_text(value):
    return value.strftime('%d.%m.%Y %H:%M') if value else '—'


class MetricCard(QFrame):
    def __init__(self, title, value='—', note='', accent=BLUE):
        super().__init__()
        self.setObjectName('metricCard')
        self.setStyleSheet(f"QFrame#metricCard{{background:white;border:1px solid {BORDER};border-radius:12px;}}")
        lay = QVBoxLayout(self); lay.setContentsMargins(18, 15, 18, 15); lay.setSpacing(7)
        top = QHBoxLayout(); label = QLabel(title); label.setStyleSheet(f'color:{MUTED};font-size:12px;font-weight:600;border:none;')
        dot = QLabel('●'); dot.setStyleSheet(f'color:{accent};border:none;')
        top.addWidget(label); top.addStretch(); top.addWidget(dot); lay.addLayout(top)
        self.value_label = QLabel(value); self.value_label.setStyleSheet(f'font-size:25px;font-weight:700;color:{TEXT};border:none;')
        self.note_label = QLabel(note); self.note_label.setStyleSheet(f'font-size:11px;color:{MUTED};border:none;')
        lay.addWidget(self.value_label); lay.addWidget(self.note_label)
    def set_value(self, value, note=None):
        self.value_label.setText(str(value))
        if note is not None: self.note_label.setText(note)


class RevenueChart(QWidget):
    """Лёгкий график на QPainter, не требует matplotlib."""
    def __init__(self, parent=None):
        super().__init__(parent); self.values = []; self.setMinimumHeight(230)
    def set_values(self, values): self.values = values; self.update()
    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(WHITE)); rect = self.rect().adjusted(36, 18, -18, -30)
        if not self.values:
            p.setPen(QColor(MUTED)); p.drawText(rect, Qt.AlignCenter, 'Нет данных о платежах за выбранный период'); return
        max_v = max([v for _, v in self.values] + [1])
        p.setPen(QPen(QColor(BORDER), 1))
        for i in range(4):
            y = rect.top() + i * rect.height() / 3
            p.drawLine(rect.left(), int(y), rect.right(), int(y))
        slot = rect.width() / max(1, len(self.values)); bar_w = min(34, slot * .55)
        for i, (label, value) in enumerate(self.values):
            h = (value / max_v) * (rect.height() - 12)
            x = rect.left() + slot * i + (slot - bar_w) / 2
            y = rect.bottom() - h
            p.setPen(Qt.NoPen); p.setBrush(QColor(BLUE)); p.drawRoundedRect(int(x), int(y), int(bar_w), max(3, int(h)), 4, 4)
            p.setPen(QColor(MUTED)); p.setFont(QFont('Segoe UI', 8)); p.drawText(int(rect.left()+slot*i), rect.bottom()+7, int(slot), 20, Qt.AlignHCenter, label)


class RentalDialog(QDialog):
    def __init__(self, customers, cars, rentals, employee, parent=None):
        super().__init__(parent); self.setWindowTitle('Новое бронирование'); self.setMinimumWidth(470)
        self.customers, self.cars, self.rentals, self.employee = customers, cars, rentals, employee
        self.result_data = None
        root = QVBoxLayout(self); title = QLabel('Создать бронирование'); title.setStyleSheet('font-size:20px;font-weight:700;color:#172B4D;')
        root.addWidget(title); form = QFormLayout(); form.setSpacing(12)
        self.customer = QComboBox()
        for c in customers: self.customer.addItem(f'{c.full_name} · {c.phone}', c.id)
        self.car = QComboBox()
        for c in cars:
            if c.status not in (CarStatus.MAINTENANCE, CarStatus.WRITTEN_OFF): self.car.addItem(f'{c.brand} {c.model} · {c.license_plate} · {money(c.price_per_day)}/день', c.id)
        self.start = QDateEdit(QDate.currentDate()); self.start.setCalendarPopup(True); self.start.setDisplayFormat('dd.MM.yyyy')
        self.end = QDateEdit(QDate.currentDate().addDays(3)); self.end.setCalendarPopup(True); self.end.setDisplayFormat('dd.MM.yyyy')
        self.deposit = QDoubleSpinBox(); self.deposit.setRange(0, 1000000); self.deposit.setSuffix(' ₽'); self.deposit.setValue(5000)
        self.cost = QLabel(); self.cost.setStyleSheet(f'font-size:18px;font-weight:700;color:{BLUE};')
        form.addRow('Клиент', self.customer); form.addRow('Автомобиль', self.car); form.addRow('Начало', self.start); form.addRow('Окончание', self.end); form.addRow('Залог (учёт)', self.deposit); form.addRow('Стоимость аренды', self.cost)
        root.addLayout(form)
        self.start.dateChanged.connect(self.recalculate); self.end.dateChanged.connect(self.recalculate); self.car.currentIndexChanged.connect(self.recalculate)
        buttons = QHBoxLayout(); buttons.addStretch(); cancel = QPushButton('Отмена'); save = QPushButton('Проверить и создать')
        save.setObjectName('primary'); cancel.clicked.connect(self.reject); save.clicked.connect(self.save); buttons.addWidget(cancel); buttons.addWidget(save); root.addLayout(buttons)
        self.recalculate()
    def recalculate(self):
        days = (self.end.date().toPyDate() - self.start.date().toPyDate()).days
        car = next((c for c in self.cars if c.id == self.car.currentData()), None)
        self.cost.setText(money(car.price_per_day * max(0, days)) if car and days > 0 else 'Проверьте даты')
    def save(self):
        customer = next((c for c in self.customers if c.id == self.customer.currentData()), None)
        car = next((c for c in self.cars if c.id == self.car.currentData()), None)
        start_d, end_d = self.start.date().toPyDate(), self.end.date().toPyDate()
        if not customer or not car: QMessageBox.warning(self, 'Не хватает данных', 'Добавьте клиента и автомобиль.'); return
        if end_d <= start_d: QMessageBox.warning(self, 'Некорректные даты', 'Окончание должно быть позже начала.'); return
        start, end = datetime.combine(start_d, datetime.min.time()), datetime.combine(end_d, datetime.min.time())
        conflicts = find_conflicts(self.rentals, car.id, start, end)
        if conflicts:
            QMessageBox.warning(self, 'Конфликт бронирования', 'Автомобиль занят в выбранный период:\n' + '\n'.join(f'{r.customer_name}: {dt_text(r.start_date)} — {dt_text(r.end_date)}' for r in conflicts)); return
        if car.status in (CarStatus.MAINTENANCE, CarStatus.WRITTEN_OFF):
            QMessageBox.warning(self, 'Автомобиль недоступен', 'Выберите другой автомобиль.'); return
        days = (end_d - start_d).days
        self.result_data = ObjectMap([('customer', customer), ('car', car), ('start', start), ('end', end),
                                      ('days', days), ('total_cost', car.price_per_day * days),
                                      ('deposit', self.deposit.value())])
        self.accept()


class ReturnDialog(QDialog):
    def __init__(self, rental, car, paid, parent=None):
        super().__init__(parent); self.setWindowTitle('Возврат автомобиля'); self.setMinimumWidth(420)
        self.rental, self.car, self.paid = rental, car, paid; self.data = None
        root = QVBoxLayout(self); title = QLabel('Оформление возврата'); title.setStyleSheet('font-size:20px;font-weight:700;color:#172B4D;'); root.addWidget(title)
        root.addWidget(QLabel(f'{rental.car_info}\nКлиент: {rental.customer_name}\nПлановый возврат: {dt_text(rental.end_date)}'))
        form = QFormLayout(); self.mileage = QSpinBox(); self.mileage.setRange(car.mileage, 2000000); self.mileage.setValue(car.mileage)
        self.payment = QDoubleSpinBox(); self.payment.setRange(0, max(0, rental.total_cost-paid)); self.payment.setDecimals(2); self.payment.setSuffix(' ₽'); self.payment.setValue(max(0, rental.total_cost-paid))
        self.method = QComboBox(); self.method.addItem('Карта', PaymentMethod.CARD); self.method.addItem('Наличные', PaymentMethod.CASH); self.method.addItem('Перевод', PaymentMethod.TRANSFER)
        form.addRow('Пробег при возврате, км', self.mileage); form.addRow('Доплата сейчас', self.payment); form.addRow('Способ оплаты', self.method); root.addLayout(form)
        root.addWidget(QLabel(f'Стоимость аренды: {money(rental.total_cost)}\nУже оплачено: {money(paid)}\nОстаток до доплаты: {money(max(0,rental.total_cost-paid))}'))
        row = QHBoxLayout(); row.addStretch(); cancel=QPushButton('Отмена'); done=QPushButton('Закрыть аренду'); done.setObjectName('primary'); cancel.clicked.connect(self.reject); done.clicked.connect(self.save); row.addWidget(cancel); row.addWidget(done); root.addLayout(row)
    def save(self):
        self.data = ObjectMap([('mileage', self.mileage.value()), ('payment', self.payment.value()), ('method', self.method.currentData())]); self.accept()


class MainWindow(QMainWindow):
    def __init__(self, storage: StorageService, report: ReportService):
        super().__init__(); self._storage, self._report = storage, report
        self._collections = self._storage.load_all(); self._current_employee = None; self._session_start = datetime.now()
        self._populate_demo_data(); self._simulate_login()
        self._report.start_session(self._current_employee.login if self._current_employee else 'unknown', self._session_start)
        self._setup_ui(); self.refresh_all()
    def _populate_demo_data(self):
        if self._collections['categories'].is_empty:
            for c in [Category('Эконом',5000,21,1500), Category('Комфорт',10000,23,2500), Category('Бизнес',25000,25,5000)]: self._collections['categories'].add(c)
        if self._collections['cars'].is_empty:
            for row in [('XTAGFK1150Y654321','Lada','Vesta','А123ВЕ777',2022,1500),('XTAGFK1150Y654322','Kia','Rio','А124КМ777',2021,1800),('XTAGFK1150Y654323','Hyundai','Solaris','А125НО777',2023,1700),('XTAGFK1150Y654324','Toyota','Camry','А126РС777',2022,3500),('XTAGFK1150Y654325','BMW','520i','А127ТУ777',2021,5500)]:
                vin, brand, model, plate, year, price = row; self._collections['cars'].add(Car(vin,brand,model,plate,self._collections['categories'].first().id,year,'белый','petrol',15000,price))
        if self._collections['customers'].is_empty:
            for name,passport,phone,lic,bday in [('Иванов Иван Иванович','1234567890','+79991234567','77АА123456',date(1990,5,15)),('Петров Петр Петрович','2345678901','+79992345678','77АА234567',date(1985,8,20)),('Сидоров Сидор Сидорович','3456789012','+79993456789','77АА345678',date(1992,3,10))]: self._collections['customers'].add(Customer(name,passport,phone,lic,bday))
        if self._collections['employees'].is_empty: self._collections['employees'].add(Employee('Администратор Админ Админович','manager','admin','admin123',date(2020,1,1),'+74951234567'))
    def _simulate_login(self): self._current_employee = self._collections['employees'].first()
    def _setup_ui(self):
        self.setWindowTitle('ПрокАвтомобилей · CRM'); self.setMinimumSize(1280, 800); self.resize(1440, 900)
        self.setStyleSheet(f"""
            QWidget {{ font-family:'Segoe UI',Arial; font-size:13px; color:{TEXT}; }} QMainWindow {{ background:{BG}; }}
            QLabel {{ background:transparent; }} QPushButton {{ background:white; border:1px solid {BORDER}; border-radius:8px; padding:9px 14px; font-weight:600; }}
            QPushButton:hover {{ border-color:{BLUE}; color:{BLUE}; }} QPushButton#primary {{ background:{BLUE}; color:white; border:0; }} QPushButton#primary:hover {{ background:#2456D6; }}
            QLineEdit,QComboBox,QDateEdit,QSpinBox,QDoubleSpinBox {{ background:white; border:1px solid {BORDER}; border-radius:7px; padding:8px; min-height:20px; }}
            QTableWidget {{ background:white; border:1px solid {BORDER}; border-radius:10px; gridline-color:#EDF1F6; selection-background-color:#EAF0FF; selection-color:{TEXT}; }}
            QHeaderView::section {{ background:#F8FAFD; color:{MUTED}; padding:10px; border:0; border-bottom:1px solid {BORDER}; font-weight:600; }}
        """)
        central=QWidget(); self.setCentralWidget(central); root=QHBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        sidebar=QFrame(); sidebar.setFixedWidth(220); sidebar.setStyleSheet(f'background:{NAVY};'); sl=QVBoxLayout(sidebar); sl.setContentsMargins(16,24,16,18); sl.setSpacing(8)
        brand=QLabel('◈  ПРОКАТ\n     CRM'); brand.setStyleSheet('color:white;font-size:19px;font-weight:800;padding:5px 8px 22px;'); sl.addWidget(brand)
        self.nav_buttons=[]; self.stack=QStackedWidget(); self.pages=[]
        for idx,(label,icon) in enumerate([('Обзор','⌂'),('Бронирования','▦'),('Выдача и возврат','↔'),('Финансы','₽'),('Автомобили','▣'),('Клиенты','♙')]):
            btn=QPushButton(f'{icon}    {label}'); btn.setCheckable(True); btn.setCursor(Qt.PointingHandCursor); btn.setStyleSheet('QPushButton{text-align:left;color:#CAD4E3;background:transparent;border:0;padding:12px;border-radius:8px;} QPushButton:checked{background:#263D5B;color:white;} QPushButton:hover{background:#203650;color:white;}')
            btn.clicked.connect(lambda checked=False, i=idx:self.navigate(i)); sl.addWidget(btn); self.nav_buttons.append(btn)
        sl.addStretch(); profile=QLabel('●  Администратор\n     Рабочая смена'); profile.setStyleSheet('color:#D5DFEB;padding:12px;border-top:1px solid #314258;'); sl.addWidget(profile)
        root.addWidget(sidebar)
        right=QWidget(); rl=QVBoxLayout(right); rl.setContentsMargins(28,24,28,24); rl.setSpacing(18)
        top=QHBoxLayout(); self.page_title=QLabel('Обзор'); self.page_title.setStyleSheet(f'font-size:26px;font-weight:800;color:{TEXT};'); top.addWidget(self.page_title); top.addStretch()
        self.global_search=QLineEdit(); self.global_search.setPlaceholderText('Поиск по арендам, клиентам, авто…'); self.global_search.setFixedWidth(300); self.global_search.textChanged.connect(self.apply_search); top.addWidget(self.global_search)
        new_btn=QPushButton('+ Новая аренда'); new_btn.setObjectName('primary'); new_btn.clicked.connect(self.create_rental); top.addWidget(new_btn); rl.addLayout(top)
        self.stack.addWidget(self.build_dashboard()); self.stack.addWidget(self.build_calendar()); self.stack.addWidget(self.build_returns()); self.stack.addWidget(self.build_finance()); self.stack.addWidget(self.build_cars()); self.stack.addWidget(self.build_customers())
        rl.addWidget(self.stack,1); root.addWidget(right,1); self.navigate(0)
    def heading(self, title, subtitle=''):
        w=QWidget(); l=QVBoxLayout(w); l.setContentsMargins(0,0,0,0); l.setSpacing(5); a=QLabel(title); a.setStyleSheet('font-size:18px;font-weight:750;'); l.addWidget(a)
        if subtitle: b=QLabel(subtitle); b.setStyleSheet(f'color:{MUTED};'); l.addWidget(b)
        return w
    def table(self, headers):
        t=QTableWidget(0,len(headers)); t.setHorizontalHeaderLabels(headers); t.setEditTriggers(QAbstractItemView.NoEditTriggers); t.setSelectionBehavior(QAbstractItemView.SelectRows); t.setSelectionMode(QAbstractItemView.SingleSelection); t.verticalHeader().setVisible(False); t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); t.setAlternatingRowColors(True); t.setSortingEnabled(False); return t
    def build_dashboard(self):
        page=QWidget(); l=QVBoxLayout(page); l.setContentsMargins(0,0,0,0); l.setSpacing(18); l.addWidget(self.heading('Сводка дня','Операционная картина автопарка и ближайшие действия'))
        cards=QGridLayout(); cards.setSpacing(14); self.m_cars=MetricCard('Автомобили'); self.m_free=MetricCard('Свободно сейчас',accent='#16A085'); self.m_active=MetricCard('Активные аренды',accent='#E9A23B'); self.m_today=MetricCard('Возвраты сегодня',accent='#E05252')
        for i,c in enumerate([self.m_cars,self.m_free,self.m_active,self.m_today]): cards.addWidget(c,0,i)
        l.addLayout(cards); l.addWidget(self.heading('Ближайшие выдачи и возвраты','Аренды, которые требуют внимания администратора'))
        self.dashboard_table=self.table(['Автомобиль','Клиент','Начало','Плановый возврат','Статус','Стоимость']); l.addWidget(self.dashboard_table,1)
        row=QHBoxLayout(); b1=QPushButton('Открыть календарь'); b1.clicked.connect(lambda:self.navigate(1)); b2=QPushButton('Обработать возвраты'); b2.clicked.connect(lambda:self.navigate(2)); row.addWidget(b1); row.addWidget(b2); row.addStretch(); l.addLayout(row); return page
    def build_calendar(self):
        page=QWidget(); l=QVBoxLayout(page); l.setContentsMargins(0,0,0,0); l.setSpacing(14); l.addWidget(self.heading('Календарь бронирований','Занятость автомобилей по дням. Конфликты проверяются при создании брони.'))
        controls=QHBoxLayout(); self.month_label=QLabel(); self.month_label.setStyleSheet('font-size:17px;font-weight:700;'); prev=QPushButton('← Предыдущий'); nxt=QPushButton('Следующий →'); prev.clicked.connect(lambda:self.shift_month(-1)); nxt.clicked.connect(lambda:self.shift_month(1)); today=QPushButton('Сегодня'); today.clicked.connect(self.reset_month); controls.addWidget(prev); controls.addWidget(today); controls.addWidget(nxt); controls.addSpacing(18); controls.addWidget(self.month_label); controls.addStretch(); l.addLayout(controls)
        self.calendar_table=self.table(['Автомобиль']+[str(i) for i in range(1,32)]); self.calendar_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        for i in range(1,32): self.calendar_table.horizontalHeader().setSectionResizeMode(i,QHeaderView.Stretch)
        self.calendar_table.setMinimumHeight(300); l.addWidget(self.calendar_table,1)
        legend=QLabel('  ■ Активная аренда    ■ Просроченная аренда    ■ Техническое обслуживание    · Свободно'); legend.setStyleSheet('color:#526176;background:white;border:1px solid #E2E8F0;border-radius:8px;padding:12px;'); l.addWidget(legend)
        self.current_month=date.today().replace(day=1); return page
    def build_returns(self):
        page=QWidget(); l=QVBoxLayout(page); l.setContentsMargins(0,0,0,0); l.setSpacing(14); l.addWidget(self.heading('Выдача и возврат','Контролируйте сроки и закрывайте аренды с фиксацией пробега и платежа.'))
        self.return_filter=QComboBox(); self.return_filter.addItems(['Все активные и просроченные','Только просроченные','Возврат сегодня']); self.return_filter.currentIndexChanged.connect(self.refresh_returns)
        row=QHBoxLayout(); row.addWidget(self.return_filter); row.addStretch(); self.payment_btn=QPushButton('Зарегистрировать платёж'); self.payment_btn.clicked.connect(self.register_selected_payment); row.addWidget(self.payment_btn); self.return_btn=QPushButton('Оформить возврат'); self.return_btn.setObjectName('primary'); self.return_btn.clicked.connect(self.process_return); row.addWidget(self.return_btn); l.addLayout(row)
        self.returns_table=self.table(['ID','Автомобиль','Клиент','Дата выдачи','Плановый возврат','Стоимость','Оплачено','Остаток','Статус']); l.addWidget(self.returns_table,1); return page
    def build_finance(self):
        page=QWidget(); l=QVBoxLayout(page); l.setContentsMargins(0,0,0,0); l.setSpacing(16); l.addWidget(self.heading('Финансы и аналитика','Учитываются зарегистрированные платежи, а не полная стоимость незакрытых договоров.'))
        cards=QGridLayout(); self.f_received=MetricCard('Получено всего',accent='#16A085'); self.f_month=MetricCard('Получено в этом месяце',accent=BLUE); self.f_debt=MetricCard('Долг по активным арендам',accent='#E05252'); self.f_avg=MetricCard('Средний чек аренды',accent='#9B59B6')
        for i,c in enumerate([self.f_received,self.f_month,self.f_debt,self.f_avg]): cards.addWidget(c,0,i)
        l.addLayout(cards); l.addWidget(self.heading('Поступления за 6 месяцев')); self.chart=RevenueChart(); chartbox=QFrame(); chartbox.setStyleSheet(f'background:white;border:1px solid {BORDER};border-radius:12px;'); cb=QVBoxLayout(chartbox); cb.addWidget(self.chart); l.addWidget(chartbox,1)
        row=QHBoxLayout(); export=QPushButton('Экспорт CSV'); export.clicked.connect(self.export_finance); row.addStretch(); row.addWidget(export); l.addLayout(row); return page
    def build_cars(self):
        page=QWidget(); l=QVBoxLayout(page); l.setContentsMargins(0,0,0,0); l.addWidget(self.heading('Автомобили','Статусы автопарка и текущие тарифы')); self.cars_table=self.table(['Марка и модель','Госномер','Год','Пробег','Цена / день','Статус']); l.addWidget(self.cars_table,1); return page
    def build_customers(self):
        page=QWidget(); l=QVBoxLayout(page); l.setContentsMargins(0,0,0,0); l.addWidget(self.heading('Клиенты','Клиентская база и контакты')); self.customers_table=self.table(['ФИО','Телефон','Водительское удостоверение','Дата рождения','Количество аренд']); l.addWidget(self.customers_table,1); return page
    def navigate(self, index):
        self.stack.setCurrentIndex(index); self.page_title.setText(['Обзор','Бронирования','Выдача и возврат','Финансы','Автомобили','Клиенты'][index])
        for i,b in enumerate(self.nav_buttons): b.setChecked(i==index)
        if index == 1: self.refresh_calendar()
        elif index == 2: self.refresh_returns()
        elif index == 3: self.refresh_finance()
    def _payments(self): return self._collections.get('payments', EntityCollection())
    def _rentals(self): return self._collections.get('rentals', EntityCollection())
    def _cars(self): return self._collections.get('cars', EntityCollection())
    def _car_for(self, rental): return next((c for c in self._cars() if c.id == rental.car_id), None)
    def refresh_all(self): self.refresh_dashboard(); self.refresh_calendar(); self.refresh_returns(); self.refresh_finance(); self.refresh_cars(); self.refresh_customers()
    def refresh_dashboard(self):
        today=date.today(); active=[r for r in self._rentals() if r.status in (RentalStatus.ACTIVE,RentalStatus.OVERDUE)]
        free=sum(1 for c in self._cars() if c.status==CarStatus.AVAILABLE and not any(r.car_id==c.id and r.status in (RentalStatus.ACTIVE,RentalStatus.OVERDUE) and r.start_date.date()<=today<r.end_date.date() for r in self._rentals()))
        due=sum(1 for r in active if r.end_date.date()==today or r.end_date.date()<today)
        self.m_cars.set_value(len(self._cars()),'в автопарке'); self.m_free.set_value(free,'доступно на сегодня'); self.m_active.set_value(len(active),'не закрыты'); self.m_today.set_value(due,'сегодня или просрочены')
        rows=[r for r in active if r.end_date.date() <= today+timedelta(days=7) or r.start_date.date() >= today]
        self.dashboard_table.setRowCount(0)
        for r in sorted(rows,key=lambda x:x.end_date)[:30]: self.add_row(self.dashboard_table,[r.car_info,r.customer_name,dt_text(r.start_date),dt_text(r.end_date),self.status_label(r),money(r.total_cost)],r.id)
    def status_label(self,r):
        if r.status==RentalStatus.CANCELLED:return 'Отменена'
        if r.status==RentalStatus.COMPLETED:return 'Завершена'
        if r.status==RentalStatus.OVERDUE or (r.status==RentalStatus.ACTIVE and r.end_date < datetime.now()): return 'Просрочена'
        return 'Активна'
    def add_row(self, table, values, key=None):
        row=table.rowCount(); table.insertRow(row)
        for col,val in enumerate(values):
            item=QTableWidgetItem(str(val)); item.setData(Qt.UserRole,key)
            if col==len(values)-1 and str(val)=='Просрочена': item.setForeground(QColor('#C53030'))
            table.setItem(row,col,item)
    def refresh_calendar(self):
        if not hasattr(self,'calendar_table'): return
        year,month=self.current_month.year,self.current_month.month; days=calendar.monthrange(year,month)[1]; self.month_label.setText(f'{calendar.month_name[month]} {year}')
        # локализованное имя месяца
        ru_months=['','января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']; self.month_label.setText(f'{ru_months[month].capitalize()} {year}')
        self.calendar_table.setColumnHidden(0,False)
        for day in range(1,32):
            self.calendar_table.setColumnHidden(day,day>days)
            self.calendar_table.setHorizontalHeaderItem(day,QTableWidgetItem(str(day)))
        cars=list(self._cars()); self.calendar_table.setRowCount(len(cars))
        for ri,car in enumerate(cars):
            self.calendar_table.setItem(ri,0,QTableWidgetItem(f'{car.brand} {car.model}\n{car.license_plate}'))
            for day in range(1,days+1):
                cell=QTableWidgetItem(''); cell.setTextAlignment(Qt.AlignCenter); cell.setFlags(cell.flags() & ~Qt.ItemIsEditable)
                d=date(year,month,day); dt=datetime.combine(d,datetime.min.time())
                if car.status==CarStatus.MAINTENANCE:
                    cell.setText('ТО'); cell.setBackground(QColor('#FFF0CC')); cell.setToolTip('Автомобиль на обслуживании')
                else:
                    rental=next((r for r in self._rentals() if r.car_id==car.id and r.status not in (RentalStatus.CANCELLED,RentalStatus.COMPLETED) and r.start_date.date()<=d<r.end_date.date()),None)
                    if rental:
                        overdue=rental.status==RentalStatus.OVERDUE or (rental.status==RentalStatus.ACTIVE and rental.end_date<datetime.now())
                        cell.setText('●'); cell.setBackground(QColor('#FDE2E2' if overdue else '#DCE7FF')); cell.setForeground(QColor('#C53030' if overdue else BLUE)); cell.setToolTip(f'{rental.customer_name}\n{dt_text(rental.start_date)} — {dt_text(rental.end_date)}\n{money(rental.total_cost)}')
                    elif d==date.today(): cell.setBackground(QColor('#F0FDF4'))
                self.calendar_table.setItem(ri,day,cell)
        self.calendar_table.resizeRowsToContents()
    def shift_month(self, delta):
        y,m=self.current_month.year,self.current_month.month+delta
        if m<1:y,m=y-1,12
        if m>12:y,m=y+1,1
        self.current_month=date(y,m,1); self.refresh_calendar()
    def reset_month(self): self.current_month=date.today().replace(day=1); self.refresh_calendar()
    def refresh_returns(self):
        if not hasattr(self,'returns_table'): return
        today=date.today(); mode=self.return_filter.currentIndex() if hasattr(self,'return_filter') else 0
        rows=[]
        for r in self._rentals():
            if r.status not in (RentalStatus.ACTIVE,RentalStatus.OVERDUE): continue
            overdue=r.status==RentalStatus.OVERDUE or r.end_date<datetime.now()
            if mode==1 and not overdue: continue
            if mode==2 and r.end_date.date()!=today and not overdue: continue
            rows.append(r)
        self.returns_table.setRowCount(0)
        for r in sorted(rows,key=lambda x:x.end_date):
            paid=paid_for_rental(self._payments(),r.id); remain=max(0,r.total_cost-paid); self.add_row(self.returns_table,[r.id[:8],r.car_info,r.customer_name,dt_text(r.start_date),dt_text(r.end_date),money(r.total_cost),money(paid),money(remain),'Просрочена' if r.end_date<datetime.now() else 'Активна'],r.id)
    def process_return(self):
        row=self.returns_table.currentRow()
        if row<0: QMessageBox.information(self,'Выберите аренду','Сначала выберите аренду в таблице.'); return
        rental_id=self.returns_table.item(row,0).data(Qt.UserRole); rental=next((r for r in self._rentals() if r.id==rental_id),None); car=self._car_for(rental) if rental else None
        if not rental or not car: QMessageBox.warning(self,'Ошибка','Не найдена аренда или автомобиль.'); return
        paid=paid_for_rental(self._payments(),rental.id); dlg=ReturnDialog(rental,car,paid,self)
        if dlg.exec_()!=QDialog.Accepted:return
        try:
            data=dlg.data
            # Валидация до регистрации платежа: ошибка пробега не должна создавать финансовую запись.
            if data['mileage'] < car.mileage: raise ValueError('Пробег при возврате не может быть меньше текущего')
            if rental.status not in (RentalStatus.ACTIVE, RentalStatus.OVERDUE): raise ValueError('Аренда уже закрыта')
            if data['payment'] > 0: register_payment(self._payments(),rental.id,data['payment'],data['method'])
            return_rental(rental,car,data['mileage'])
            self._save_data(); self.refresh_all(); QMessageBox.information(self,'Возврат оформлен',f'Аренда закрыта.\nПробег: {car.mileage:,} км\nОстаток после платежа: {money(max(0,rental.total_cost-paid_for_rental(self._payments(),rental.id)))}'.replace(',',' '))
        except Exception as exc: QMessageBox.critical(self,'Не удалось оформить возврат',str(exc))
    def register_selected_payment(self):
        row = self.returns_table.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Выберите аренду', 'Выберите аренду, к которой относится платёж.')
            return
        rental_id = self.returns_table.item(row, 0).data(Qt.UserRole)
        rental = next((r for r in self._rentals() if r.id == rental_id), None)
        if not rental:
            QMessageBox.warning(self, 'Ошибка', 'Аренда не найдена.')
            return
        paid = paid_for_rental(self._payments(), rental.id)
        remaining = max(0.0, rental.total_cost - paid)
        if remaining <= 0:
            QMessageBox.information(self, 'Задолженности нет', 'Стоимость аренды уже полностью оплачена.')
            return
        dlg = QDialog(self); dlg.setWindowTitle('Регистрация платежа'); dlg.setMinimumWidth(360)
        layout = QVBoxLayout(dlg); layout.addWidget(QLabel(f'{rental.car_info}\nКлиент: {rental.customer_name}\nСтоимость: {money(rental.total_cost)}\nУже оплачено: {money(paid)}\nОстаток: {money(remaining)}'))
        form = QFormLayout(); amount = QDoubleSpinBox(); amount.setRange(0.01, max(0.01, remaining)); amount.setDecimals(2); amount.setSuffix(' ₽'); amount.setValue(min(remaining, 10000000))
        method = QComboBox(); method.addItem('Карта', PaymentMethod.CARD); method.addItem('Наличные', PaymentMethod.CASH); method.addItem('Перевод', PaymentMethod.TRANSFER)
        form.addRow('Сумма платежа', amount); form.addRow('Способ оплаты', method); layout.addLayout(form)
        buttons = QHBoxLayout(); buttons.addStretch(); cancel = QPushButton('Отмена'); save = QPushButton('Зарегистрировать'); save.setObjectName('primary'); cancel.clicked.connect(dlg.reject); save.clicked.connect(dlg.accept); buttons.addWidget(cancel); buttons.addWidget(save); layout.addLayout(buttons)
        if dlg.exec_() != QDialog.Accepted: return
        try:
            register_payment(self._payments(), rental.id, amount.value(), method.currentData())
            self._save_data(); self.refresh_all()
            QMessageBox.information(self, 'Платёж зарегистрирован', f'Зарегистрировано: {money(amount.value())}.\nНовый остаток: {money(max(0, rental.total_cost-paid_for_rental(self._payments(), rental.id)))}')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка платежа', str(exc))

    def refresh_finance(self):
        if not hasattr(self,'chart'):return
        payments=[p for p in self._payments() if p.status==PaymentStatus.COMPLETED]
        total=sum(p.amount for p in payments); now=date.today(); month_total=sum(p.amount for p in payments if p.payment_date.year==now.year and p.payment_date.month==now.month)
        debt=sum(max(0,r.total_cost-paid_for_rental(self._payments(),r.id)) for r in self._rentals() if r.status in (RentalStatus.ACTIVE,RentalStatus.OVERDUE))
        completed=[r for r in self._rentals() if r.status==RentalStatus.COMPLETED]; avg=sum(r.total_cost for r in completed)/len(completed) if completed else 0
        self.f_received.set_value(money(total),'подтверждённые платежи'); self.f_month.set_value(money(month_total),'за текущий месяц'); self.f_debt.set_value(money(debt),'по активным договорам'); self.f_avg.set_value(money(avg),'по завершённым арендам')
        vals=[]; months=[]
        for offset in range(5,-1,-1):
            y,m=now.year,now.month-offset
            while m<=0:y-=1;m+=12
            months.append((y,m))
        short=['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек']
        for y,m in months: vals.append((short[m-1],sum(p.amount for p in payments if p.payment_date.year==y and p.payment_date.month==m)))
        self.chart.set_values(vals)
    def refresh_cars(self):
        if not hasattr(self,'cars_table'):return
        self.cars_table.setRowCount(0); labels=ObjectMap([(CarStatus.AVAILABLE,'Свободен'),(CarStatus.RENTED,'В аренде'),(CarStatus.MAINTENANCE,'На ТО'),(CarStatus.WRITTEN_OFF,'Списан')])
        for c in self._cars(): self.add_row(self.cars_table,[f'{c.brand} {c.model}',c.license_plate,c.year,f'{c.mileage:,} км'.replace(',',' '),money(c.price_per_day),labels.get(c.status,c.status)],c.id)
    def refresh_customers(self):
        if not hasattr(self,'customers_table'):return
        self.customers_table.setRowCount(0)
        for c in self._collections['customers']:
            count=sum(1 for r in self._rentals() if r.customer_id==c.id); self.add_row(self.customers_table,[c.full_name,c.phone,c.driver_license,c.birth_date.strftime('%d.%m.%Y'),count],c.id)
    def create_rental(self):
        if not self._current_employee: QMessageBox.warning(self,'Нет сотрудника','Добавьте сотрудника перед оформлением аренды.'); return
        dlg=RentalDialog(self._collections['customers'],self._cars(),self._rentals(),self._current_employee,self)
        if dlg.exec_()!=QDialog.Accepted:return
        d=dlg.result_data; r=Rental(d['customer'].id,d['customer'].full_name,d['car'].id,f'{d["car"].brand} {d["car"].model} [{d["car"].license_plate}]',self._current_employee.id,self._current_employee.login,d['start'],d['end'],d['days'],d['total_cost'])
        try:
            self._rentals().add(r)
            # Текущий статус «в аренде» только если интервал включает сегодня; будущая бронь остаётся свободной по статусу, но проверяется календарём.
            if d['start'] <= datetime.now() < d['end']: d['car'].mark_rented()
            self._save_data(); self.refresh_all(); QMessageBox.information(self,'Бронирование создано',f'{r.car_info}\n{dt_text(r.start_date)} — {dt_text(r.end_date)}\nСтоимость: {money(r.total_cost)}')
        except Exception as exc: QMessageBox.critical(self,'Ошибка сохранения',str(exc))
    def apply_search(self, text):
        # Поиск применяется к таблице текущего раздела без изменения исходных данных.
        table=self.stack.currentWidget().findChild(QTableWidget)
        if not table:return
        query=text.strip().casefold()
        for row in range(table.rowCount()):
            visible=not query or any(query in (table.item(row,col).text().casefold() if table.item(row,col) else '') for col in range(table.columnCount()))
            table.setRowHidden(row,not visible)
    def export_finance(self):
        from PyQt5.QtWidgets import QFileDialog
        path,_=QFileDialog.getSaveFileName(self,'Экспорт платежей','payments.csv','CSV (*.csv)')
        if not path:return
        import csv
        try:
            with open(path,'w',newline='',encoding='utf-8-sig') as f:
                w=csv.writer(f,delimiter=';'); w.writerow(['Дата','ID аренды','Сумма','Способ','Статус'])
                for p in sorted(self._payments(),key=lambda x:x.payment_date): w.writerow([p.payment_date.strftime('%d.%m.%Y %H:%M'),p.rental_id,p.amount,p.method,p.status])
            QMessageBox.information(self,'Экспорт завершён',f'Файл сохранён:\n{path}')
        except OSError as exc: QMessageBox.critical(self,'Ошибка экспорта',str(exc))
    def _save_data(self):
        if not self._storage.save_all(self._collections): raise RuntimeError('Не удалось сохранить data.json. Проверьте права доступа и свободное место.')
    def closeEvent(self, event):
        answer = QMessageBox.question(
            self, 'Выход', 'Сохранить изменения и закрыть приложение?',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes
        )
        if answer == QMessageBox.Cancel:
            event.ignore()
            return
        try:
            if answer == QMessageBox.Yes:
                self._save_data()
            # Отчёт о рабочей сессии обязателен при любом подтверждённом закрытии.
            self._report.finish_session(datetime.now())
            if not self._report.save_to_file():
                raise RuntimeError('Не удалось сохранить отчёт о рабочей сессии.')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка сохранения', str(exc))
            event.ignore()
            return
        event.accept()

"""Бизнес-правила аренды, возврата и платежей. Совместимо с текущими JSON-сущностями."""
from datetime import datetime
from entities import RentalStatus, CarStatus, Payment, PaymentMethod, PaymentStatus


def overlaps(start, end, other_start, other_end):
    """Полуоткрытые интервалы: окончание одной аренды совпадает с началом следующей без конфликта."""
    return start < other_end and other_start < end


def find_conflicts(rentals, car_id, start, end, exclude_id=None):
    conflicts = []
    for rental in rentals:
        if rental.id == exclude_id or rental.car_id != car_id:
            continue
        if rental.status in (RentalStatus.CANCELLED, RentalStatus.COMPLETED):
            continue
        if overlaps(start, end, rental.start_date, rental.end_date):
            conflicts.append(rental)
    return conflicts


def return_rental(rental, car, mileage, return_time=None):
    """Закрывает аренду и обновляет пробег/статус автомобиля."""
    if rental.status not in (RentalStatus.ACTIVE, RentalStatus.OVERDUE):
        raise ValueError("Вернуть можно только активную или просроченную аренду")
    if mileage < car.mileage:
        raise ValueError("Пробег при возврате не может быть меньше текущего")
    car.mileage = int(mileage)
    rental.complete(return_time or datetime.now())
    # Не освобождаем машину, если она находится в ремонте/списана.
    if car.status == CarStatus.RENTED:
        car.mark_available()


def register_payment(collection, rental_id, amount, method=PaymentMethod.CARD, payment_date=None):
    if amount <= 0:
        raise ValueError("Сумма платежа должна быть больше нуля")
    payment = Payment(rental_id, float(amount), method,
                      payment_date=payment_date or datetime.now(),
                      status=PaymentStatus.COMPLETED)
    collection.add(payment)
    return payment


def paid_for_rental(payments, rental_id):
    total = 0.0
    for payment in payments:
        if payment.rental_id == rental_id and payment.status == PaymentStatus.COMPLETED:
            total += payment.amount
        elif payment.rental_id == rental_id and payment.status == PaymentStatus.REFUNDED:
            total -= payment.amount
    return max(0.0, total)

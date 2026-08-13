from celery import shared_task
from .models import Payment


@shared_task
def process_mock_payment(payment_id: int):
    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        return None
    payment.status = "succeeded"
    payment.save()
    return payment.id

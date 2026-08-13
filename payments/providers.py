from .models import Payment
from orders.models import Order
from .tasks import process_mock_payment


class PaymentProvider:
    def create_payment(self, order: Order, amount: float) -> Payment:
        raise NotImplementedError()

    def handle_webhook(self, data: dict) -> Payment:
        raise NotImplementedError()


class MockPaymentProvider(PaymentProvider):
    def create_payment(self, order: Order, amount: float) -> Payment:
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            provider="mock",
            status="pending",
        )
        process_mock_payment.delay(payment.id)
        return payment

    def handle_webhook(self, data: dict) -> Payment:
        payment_id = data.get("payment_id")
        status = data.get("status", "succeeded")
        payment = Payment.objects.filter(id=payment_id).first()
        if payment:
            payment.status = status
            payment.save()
        return payment

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer, PaymentStatusUpdateSerializer


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(provider="mock", status="succeeded")
        if payment.order.status == "pending":
            payment.order.status = "paid"
            payment.order.save(update_fields=["status"])


class PaymentWebhookView(generics.GenericAPIView):
    serializer_class = PaymentStatusUpdateSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get("payment_id")
        status_value = request.data.get("status", "succeeded")
        payment = Payment.objects.filter(id=payment_id).first()
        if not payment:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )
        payment.status = status_value
        payment.save()
        if status_value == "succeeded":
            payment.order.status = "paid"
            payment.order.save(update_fields=["status"])
        return Response({"detail": "Payment status updated."})

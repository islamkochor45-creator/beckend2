from django.urls import path
from .views import PaymentCreateView, PaymentWebhookView

urlpatterns = [
    path("create/", PaymentCreateView.as_view(), name="payment-create"),
    path("webhook/mock/", PaymentWebhookView.as_view(), name="mock-payment-webhook"),
]

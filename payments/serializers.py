from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "status",
            "provider",
            "external_id",
            "amount",
            "created_at",
        ]
        read_only_fields = ["status", "external_id", "created_at"]

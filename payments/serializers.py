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

    def validate(self, attrs):
        request = self.context["request"]
        order = attrs["order"]
        if order.user != request.user:
            raise serializers.ValidationError({"order": "Заказ вам не принадлежит."})
        if attrs["amount"] != order.total_amount:
            raise serializers.ValidationError({"amount": "Сумма не совпадает с заказом."})
        return attrs


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payment
        fields = ["status"]
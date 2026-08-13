from rest_framework import serializers
from .models import Address, Order, OrderItem


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "city",
            "street",
            "house",
            "apartment",
            "postal_code",
            "is_default",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "seller", "quantity", "price_at_purchase"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "status",
            "total_amount",
            "commission_amount",
            "items",
        ]
        read_only_fields = ["user", "status", "total_amount", "commission_amount"]

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        address = Address.objects.create(
            user=self.context["request"].user, **address_data
        )
        order = Order.objects.create(
            user=self.context["request"].user, address=address, **validated_data
        )
        return order

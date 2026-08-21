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

    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

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
        read_only_fields = [
            "user",
            "status",
            "total_amount",
            "commission_amount",
        ]

    def validate_address(self, address):
        if address.user != self.context["request"].user:
            raise serializers.ValidationError("Этот адрес вам не принадлежит.")
        return address

    # def create(self, validated_data):
    #     return Order.objects.create(
    #         user=self.context["request"].user,
    #         **validated_data
    #     )
    def create(self, validated_data):
        validated_data.pop("user", None)

        return Order.objects.create(user=self.context["request"].user, **validated_data)

from decimal import Decimal

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Order, OrderItem, Address
from .serializers import OrderSerializer, AddressSerializer

from cart.models import Cart


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CheckoutView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        # 1. Получаем ID адреса
        address_id = request.data.get("address")

        if not address_id:
            raise ValidationError({"address": "Укажите адрес доставки."})

        # 2. Проверяем, что адрес принадлежит пользователю
        address = Address.objects.filter(id=address_id, user=request.user).first()

        if not address:
            raise ValidationError({"address": "Адрес не найден."})

        # 3. Получаем корзину пользователя
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            raise ValidationError({"cart": "Корзина не найдена."})

        # 4. Получаем товары корзины
        cart_items = cart.items.select_related("product", "product__seller").all()

        if not cart_items.exists():
            raise ValidationError({"cart": "Корзина пуста."})

        # 5. Считаем общую сумму
        total_amount = sum(
            (item.product.price * item.quantity for item in cart_items), Decimal("0.00")
        )

        # 6. Комиссия магазина — 10%
        commission_rate = Decimal("0.10")

        commission_amount = total_amount * commission_rate

        # 7. Создаём Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            status="pending",
            total_amount=total_amount,
            commission_amount=commission_amount,
        )

        # 8. Создаём OrderItem
        for cart_item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                seller=cart_item.product.seller,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price,
            )

        # 9. Очищаем корзину
        cart.items.all().delete()

        # 10. Возвращаем созданный заказ
        serializer = self.get_serializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def delete(self, request, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, id=kwargs["pk"]).first()
        if not order:
            return Response(
                {"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND
            )
        if order.status != "pending":
            return Response(
                {
                    "detail": "Невозможно удалить заказ, который не находится в статусе 'pending'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

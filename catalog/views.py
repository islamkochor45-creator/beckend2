from django.db.models import F, Sum
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from .models import Category, Product, Seller, FavoriteItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    SellerSerializer,
    FavoriteItemSerializer,
    ProductImageUploadSerializer,
)
from core.permissions import IsSeller


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["category", "seller"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name"]
    ordering = ["name"]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["get", "head", "options"]


class SellerListView(generics.ListAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [permissions.AllowAny]


class SellerProductSerializer(ProductSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    slug = serializers.CharField(read_only=True)


class SellerProductListCreateView(generics.ListCreateAPIView):
    serializer_class = SellerProductSerializer
    permission_classes = [IsSeller]

    def get_seller(self):
        return get_object_or_404(Seller, user=self.request.user)

    def get_queryset(self):
        return Product.objects.filter(seller=self.get_seller())

    def perform_create(self, serializer):
        seller = self.get_seller()
        name = serializer.validated_data["name"]
        base_slug = slugify(name) or f"product-{self.request.user.pk}"
        slug = base_slug
        suffix = 2
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        serializer.save(seller=seller, slug=slug)


class SellerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SellerProductSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return Product.objects.filter(seller=seller)


class SellerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerSerializer
    permission_classes = [IsSeller]

    def get_object(self):
        return get_object_or_404(Seller, user=self.request.user)


class SellerProductImageView(generics.ListCreateAPIView):
    serializer_class = ProductImageUploadSerializer
    permission_classes = [IsSeller]

    def get_product(self):
        seller = get_object_or_404(Seller, user=self.request.user)
        return get_object_or_404(Product, id=self.kwargs["product_id"], seller=seller)

    def get_queryset(self):
        return self.get_product().images.all()

    def perform_create(self, serializer):
        serializer.save(product=self.get_product())


class SellerStatsView(generics.GenericAPIView):
    permission_classes = [IsSeller]

    def get(self, request, *args, **kwargs):
        seller = get_object_or_404(Seller, user=request.user)
        from orders.models import OrderItem

        items = OrderItem.objects.filter(seller=seller).exclude(order__status="cancelled")
        totals = items.aggregate(
            sales_count=Sum("quantity"),
            revenue=Sum(F("quantity") * F("price_at_purchase")),
        )
        return Response(
            {
                "products_count": Product.objects.filter(seller=seller).count(),
                "sales_count": totals["sales_count"] or 0,
                "revenue": totals["revenue"] or 0,
            }
        )


class SellerOrdersView(generics.GenericAPIView):
    permission_classes = [IsSeller]

    def get(self, request, *args, **kwargs):
        seller = get_object_or_404(Seller, user=request.user)
        from orders.models import OrderItem

        items = (
            OrderItem.objects.filter(seller=seller)
            .exclude(order__status="cancelled")
            .select_related("order", "product")
        )
        return Response(
            [
                {
                    "id": item.order_id,
                    "order": item.order_id,
                    "product": {"id": item.product_id, "name": item.product.name},
                    "quantity": item.quantity,
                    "status": item.order.status,
                }
                for item in items
            ]
        )


class SellerOrderStatusView(generics.GenericAPIView):
    permission_classes = [IsSeller]

    def patch(self, request, *args, **kwargs):
        from orders.models import Order

        seller = get_object_or_404(Seller, user=request.user)
        order = get_object_or_404(
            Order,
            id=kwargs["order_id"],
            items__seller=seller,
        )
        new_status = request.data.get("status")
        allowed = {choice[0] for choice in Order.STATUS_CHOICES}
        if new_status not in allowed:
            return Response({"detail": "Недопустимый статус заказа."}, status=400)
        order.status = new_status
        order.save(update_fields=["status"])
        return Response({"id": order.id, "status": order.status})


class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteItem.objects.filter(user=self.request.user)


class FavoriteCreateView(generics.CreateAPIView):
    serializer_class = FavoriteItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        if not product_id:
            return Response(
                {"detail": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        favorite, created = FavoriteItem.objects.get_or_create(
            user=request.user, product=product
        )

        if created:
            serializer = self.get_serializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "Product already in favorites."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        favorite_id = self.kwargs.get("pk")
        return get_object_or_404(FavoriteItem, id=favorite_id, user=self.request.user)

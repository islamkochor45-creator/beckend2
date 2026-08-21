from rest_framework import serializers
from .models import (
    Category,
    Product,
    ProductImage,
    ProductAttribute,
    Seller,
    FavoriteItem,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent"]


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "company_name", "is_verified", "logo", "user"]
        read_only_fields = ["id", "user", "is_verified"]


class ProductImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]
        read_only_fields = ["id"]


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]

    def get_image(self, obj):
        if not obj.image:
            return None

        return obj.image.url


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["id", "name", "value"]


class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source="seller.company_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "seller",
            "seller_name",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "avg_rating",
            "reviews_count",
            "images",
            "attributes",
        ]


class FavoriteItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = FavoriteItem
        fields = ["id", "product", "product_name", "product_price", "created_at"]
        read_only_fields = ["created_at"]

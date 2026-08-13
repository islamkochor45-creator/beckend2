from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "rating",
            "text",
            "is_moderated",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "is_moderated", "created_at", "updated_at"]

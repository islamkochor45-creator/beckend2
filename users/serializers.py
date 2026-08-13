from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Явно делаем необязательным — иначе ModelSerializer наследует
    # required=True от поля модели, и форма без username падает с 400.
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "role"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        username = (
            validated_data.get("username") or validated_data["email"].split("@")[0]
        )
        user = User.objects.create_user(
            email=validated_data["email"],
            username=username,
            password=validated_data["password"],
            role=validated_data.get("role", "buyer"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "role"]


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

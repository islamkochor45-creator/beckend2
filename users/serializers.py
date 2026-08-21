from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from catalog.models import Seller

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    # Явно делаем необязательным — иначе ModelSerializer наследует
    # required=True от поля модели, и форма без username падает с 400.
    username = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "password2",
            "role",
            "company_name",
        ]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data):
        company_name = validated_data.pop("company_name", "")
        validated_data.pop("password2", None)
        username = (
            validated_data.get("username") or validated_data["email"].split("@")[0]
        )
        user = User.objects.create_user(
            email=validated_data["email"],
            username=username,
            password=validated_data["password"],
            role=validated_data.get("role", "buyer"),
        )
        user.email_user(
            "Welcome to Internet Shops",
            f"Hello {user.username},\n\nWelcome to Internet Shops! Your account has been created successfully.",
        )
        if user.role == "seller":
            Seller.objects.create(
                user=user,
                company_name=company_name or user.username,
            )
        return user

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        validate_password(attrs["new_password"])
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "role"]


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

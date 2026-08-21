from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Category, Product, Seller
from users.models import User


class MarketplaceApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Дом", slug="home")
        self.seller_user = User.objects.create_user(
            email="seller@example.com",
            username="seller",
            password="StrongPass123!",
            role="seller",
        )
        self.seller = Seller.objects.create(
            user=self.seller_user,
            company_name="Test Shop",
        )
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            username="buyer",
            password="StrongPass123!",
        )
        Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Wooden bowl",
            slug="wooden-bowl",
            price="10.00",
        )

    def test_register_seller_creates_profile(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "new-seller@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "seller",
                "company_name": "New Shop",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="new-seller@example.com")
        self.assertTrue(Seller.objects.filter(user=user, company_name="New Shop").exists())

    def test_catalog_search_and_category_filter(self):
        response = self.client.get(
            "/api/catalog/products/",
            {"search": "wooden", "category": self.category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_buyer_cannot_use_seller_products_endpoint(self):
        self.client.force_authenticate(self.buyer)
        response = self.client.get("/api/catalog/seller/products/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seller_can_create_product_without_seller_or_slug(self):
        self.client.force_authenticate(self.seller_user)
        response = self.client.post(
            "/api/catalog/seller/products/",
            {
                "name": "Clay cup",
                "category": self.category.id,
                "price": "12.50",
                "stock": 4,
                "description": "Handmade cup",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["seller"], self.seller.id)

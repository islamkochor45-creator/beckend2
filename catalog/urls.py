from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView,
    ProductListView,
    ProductDetailView,
    SellerListView,
    FavoriteListView,
    FavoriteCreateView,
    FavoriteDeleteView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("sellers/", SellerListView.as_view(), name="seller-list"),
    path("favorites/", FavoriteListView.as_view(), name="favorite-list"),
    path("favorites/add/", FavoriteCreateView.as_view(), name="favorite-create"),
    path("favorites/<int:pk>/", FavoriteDeleteView.as_view(), name="favorite-delete"),
]

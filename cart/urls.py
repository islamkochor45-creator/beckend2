from django.urls import path
from .views import CartDetailView, CartItemCreateView, CartItemDetailView

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart-detail"),
    path("items/", CartItemCreateView.as_view(), name="cartitem-create"),
    path("items/<int:pk>/", CartItemDetailView.as_view(), name="cartitem-detail"),
]

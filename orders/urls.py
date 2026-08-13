from django.urls import path
from .views import OrderListCreateView, OrderDetailView, AddressListCreateView

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("addresses/", AddressListCreateView.as_view(), name="address-list"),
]

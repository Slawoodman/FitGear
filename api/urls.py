from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("routes/", views.RoutesAPIView.as_view(), name="routes"),
    path("products/", views.ProductsAPIView.as_view(), name="products"),
    path("products/<int:pk>/", views.ProductAPIView.as_view(), name="product"),
    path(
        "products/<int:pk>/order/create/",
        views.CreateOrderAPIView.as_view(),
        name="create_order",
    ),
    path("orders/", views.OrdersAPIView.as_view(), name="orders"),
    path("orders/<int:pk>/", views.OrderAPIView.as_view(), name="order"),
    path(
        "orders/<int:pk>/payment/",
        views.OrderPaymentAPIView.as_view(),
        name="order_payment",
    ),
    path(
        "orders/<int:pk>/gen-bill/",
        views.OrderGenBillAPIView.as_view(),
        name="order_gen_bill",
    ),
    path(
        "orders/<int:pk>/change-status/",
        views.ChangeOrderStatusAPIView.as_view(),
        name="change_order_status",
    ),
    path("users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

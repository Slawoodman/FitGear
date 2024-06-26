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
    
    path("cart/", views.CartAPIView.as_view(),name="view-cart"),
    path("cart/add-to-cart/<int:pk>/<int:quantity>/", views.AddToCartAPIView.as_view(), name="add-to-cart"),
    path("cart/update-cart-item/<int:pk>/<int:quantity>/", views.UpdateCartItemAPIView.as_view(), name="update-cart-item"),
    path("cart/remove-from-cart/<int:cart_item_id>/", views.RemoveFromCartAPIView.as_view(), name="remove-from-cart"),

    path("orders/", views.OrdersAPIView.as_view(), name="orders"),
    path("order/<int:pk>/", views.OrderAPIView.as_view(), name="order"),
    path("order/create-order/", views.CreateOrderAPIView.as_view(),name="create-order"),
    path(
        "order/<int:pk>/payment/",
        views.OrderPaymentAPIView.as_view(),
        name="order_payment",
    ),
    path(
        "order/<int:pk>/gen-bill/",
        views.OrderGenBillAPIView.as_view(),
        name="order_gen_bill",
    ),
    path(
        "order/<int:pk>/change-status/",
        views.ChangeOrderStatusAPIView.as_view(),
        name="change_order_status",
    ),
    path("users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/login/', views.LoginUserAPIView.as_view(), name='api_login'),
    path('api/register/', views.RegisterUserAPIView.as_view(), name='api_register'),
    path('api/logout/', views.LogoutUserAPIView.as_view(), name='api_logout'),
]

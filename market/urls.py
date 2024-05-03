from django.urls import path
from . import views

urlpatterns = [
    path("", views.MainPageView.as_view(), name="main"),
    path("product/<str:pk>", views.ProductView.as_view(), name="product-view"),
    path("order/<str:pk>", views.CreateUserOrderView.as_view(), name="user-order"),
    path("orders/", views.GetOrdersView.as_view(), name="showorders"),
    path("checkout/<int:pk>", views.MarkOrderItemAsPaidView.as_view(), name="checkout"),


    path("cart/", views.CartView.as_view(), name="cart"),
    path("add-item/<int:pk>", views.AddToCartView.as_view(), name="add-to-cart"),
    path('update-cart-item/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    path("remove-item/<int:cart_item_id>", views.RemoveFromCartView.as_view(), name="remove-item"),
    path(
        "payment/<int:pk>", views.GeneratePaymentHtmlView.as_view(), name="genpayment"
    ),
    path("download_file/<int:pk>", views.DownloadFileView.as_view(), name="view_html"),
    path(
        "orders/<int:pk>/change_status/",
        views.ChangeOrderStatusView.as_view(),
        name="change_status",
    ),
]

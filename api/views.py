from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductSerializer, OrderItemSerializer, OrderSerializer, CartSerializer
from market.models import Product, OrderItem, Cart, CartItem
from market.forms import OrderCreatForm
from users.models import User
from .utils import filter_orders_by_role


from drf_spectacular.utils import extend_schema


class RoutesAPIView(APIView):
    @extend_schema(
        description="""
            Get available routes.

            Returns a list of available routes in the API.

            Example response:
                [{"GET": "/api/routes/"}]
        """,
        responses={200: OpenApiExample([{"GET": "/api/routes/"}])},
        tags=["Routes"],
    )
    def get(self, request):
        """
        Get available routes.
        """

        routes = [
            {"GET": "/api/routes/"},
            {"GET": "/api/products/"},
            {"GET": "/api/products/<int:pk>/"},
            {"GET": "/api/orders/"},
            {"GET": "/api/orders/<int:pk>/"},
            {"POST": "/api/products/<int:pk>/order/create/"},
            {"POST": "/api/orders/<int:pk>/payment/"},
            {"POST": "/api/orders/<int:pk>/gen-bill/"},
            {"POST": "/api/orders/<int:pk>/change-status/"},
            {"POST": "/api/users/token/"},
            {"POST": "/api/users/token/refresh/"},
        ]
        return Response(routes)


class ProductsAPIView(APIView):
    @extend_schema(
        description="""
                Get all products.
                Returns a list of all products available in the system.
            """,
        responses={200: ProductSerializer(many=True)},
        tags=["Products"],
    )
    def get(self, request):
        """
        Get all products.
        """
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductAPIView(APIView):
    @extend_schema(
        description="""
            Get a product by ID.

            Returns the product details for the specified ID.

            Parameters:
                - `pk` (int): The ID of the product.

            Example response:
            {
                "id": 1,
                "name": "Product 1",
                "price": 10.99,
                ...
            }
        """,
        responses={200: ProductSerializer()},
        tags=["Products"],
    )
    def get(self, request, pk):
        """
        Get a product by ID.
        Returns the product details for the specified ID.
        """
        product = get_object_or_404(Product, id=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class CartAPIView(APIView):
    @extend_schema(
        description="""
        API endpoint for retrieving the user's cart.
        
        Retrieves the user's cart details.
        
        Responses:
        
            - 200 OK: Returns the user's cart details.
        """
        ,
        tags=["Cart"],
    )

    def get(self, request):
        """
        Retrieve the user's cart details.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCartAPIView(APIView):
    @extend_schema(
        description="Add a product to the user's cart. Increments the quantity of a specified product in the user's cart by the specified quantity.",
        responses={
            status.HTTP_204_NO_CONTENT: "Product added to cart successfully."
        },
        tags=["Cart"],
        request={
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "The ID of the product to add to the cart.",
                    "required": True
                },
                "quantity": {
                    "type": "integer",
                    "description": "The quantity of the product to add. Defaults to 1.",
                    "required": True,
                    "default": 1
                }
            }
        }
    )
    def post(self, request, pk, quantity):
        product_id = pk
        quantity = quantity

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


# class UpdateCartItemAPIView(APIView):
#     @extend_schema(
#         description="""
#             Update the quantity of a product in the user's cart.

#             Updates the quantity of a specified product in the user's cart to the specified quantity.

#             Request Body:
#                 {
#                     "item_id": int,  # The ID of the cart item to update.
#                     "quantity": int  # The new quantity of the product.
#                 }

#             Returns:
#                 - `success` (bool): Indicates if the update was successful.
#                 - `total_price` (float): The updated total price of the cart.
#         """,
#         responses={status.HTTP_200_OK: {"success": True, "total_price": 123.45}},
#         tags=["Cart"],
#     )
#     def post(self, request):
#         data = request.data
#         item_id = data.get('item_id')
#         new_quantity = data.get('quantity')
#         try:
#             cart_item = CartItem.objects.get(id=item_id)
#             cart_item.quantity = new_quantity
#             cart_item.price_sum = cart_item.quantity * cart_item.product.price
#             cart_item.save()
#             cart = cart_item.cart
#             for item in cart.items.all():
#                 item.price_sum = item.product.price * item.quantity
#                 item.save()
#             total_price = sum([item.price_sum for item in cart.items.all()])
#             return Response({'success': True, 'total_price': total_price})
#         except CartItem.DoesNotExist:
#             return Response({'success': False, 'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromCartAPIView(APIView):
    @extend_schema(
        description="""
            Remove a product from the user's cart.

            Deletes the specified product from the user's cart.

            Parameters:
                - `cart_item_id` (int): The ID of the cart item to remove.

            Returns:
                HTTP 204 No Content if the product is successfully removed from the cart.
        """,
        responses={status.HTTP_204_NO_CONTENT: "Product removed from cart successfully."},
        tags=["Cart"],
    )
    def delete(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="""
            Get orders based on user role.

            Returns a list of orders based on the user's role.

            Available roles:
                - Admin: All orders
                - User: Orders that have been ordered by the current user

            Example response:
            [
                {
                    "id": 1,
                    "customer": "John Doe",
                    "status": "Undecided",
                    ...
                },
                ...
            ]
        """,
        responses={200: OrderSerializer(many=True)},
        tags=["Orders"],
    )
    def get(self, request):
        """
        Get orders based on user role.
        Returns a list of orders based on the user's role.
        """
        user = request.user
        orders = filter_orders_by_role(user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="""
            Get an order by ID.

            Returns the details of the specified order.

            Parameters:
                - `pk` (int): The ID of the order.

            Example response:
            {
                "id": 1,
                "customer": "John Doe",
                "status": "Pending",
            }
        """,
        responses={200: OrderItemSerializer()},
        tags=["Orders"],
    )
    def get(self, request, pk):
        """
        Get an order by ID.
        Returns the details of the specified order.

        """
        order = get_object_or_404(OrderItem, id=pk)
        serializer = OrderItemSerializer(order)
        return Response(serializer.data)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="""
            Create a new order, only User can create one.
            Creates a new order for the specified product.

            Parameters:
                - `pk` (int): The ID of the product.

            Example request body:
                {
                    "address": "U address",
                    "postal_code": "U postal_code",
                    "city": "U city name",
                }

            Example response:
                "New order created successfully!
        """,
        responses={201: "New order created successfully!"},
        tags=["Products"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "address": {"type": "string", "example": "U'r address"},
                    "postal_code": {"type": "string", "example": "U'r postal_code"},
                    "city": {"type": "string", "example": "U'r city name"},
                },
                "required": ["status"],
            },
        },
    )
    def post(self, request, pk):
        """
        Creates a new order for the specified product.
        """
        user = request.user
        role = user.role
        item = get_object_or_404(Product, id=pk)

        if role == User.Role.USER:
            form = OrderCreatForm(request.data)

            if form.is_valid():
                new_order = form.save(commit=False)
                new_order.customer = user
                new_order.product = item
                new_order.save()

                return Response(
                    "New order created successfully!", status=status.HTTP_201_CREATED
                )
            else:
                return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                "Only users can create a new order.", status=status.HTTP_403_FORBIDDEN
            )


class OrderPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="""
            Pay for an order.

            Processes the payment for the specified order.

            Parameters:
                - `pk` (int): The ID of the order.

            Example response:
                "Payment successful."
        """,
        responses={200: "Payment successful."},
        tags=["Orders"],
    )
    def post(self, request, pk):
        """
        Processes the payment for the specified order.
        """
        order_item = get_object_or_404(OrderItem, id=pk)
        user = request.user
        role = user.role

        if role == User.Role.USER and order_item.customer == user:
            try:
                order_item.status_to_pading()
                return Response("Payment successful.", status=status.HTTP_200_OK)
            except:
                return Response(
                    "An error occurred.", status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            "Only owners can pay for the order.", status=status.HTTP_403_FORBIDDEN
        )


class OrderGenBillAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="""
            Generate a bill for an order.

            Generates a bill for the specified order.

            Parameters:
                - `pk` (int): The ID of the order.

            Example response:
                "Payment is created..."
        """,
        responses={200: "Payment is created..."},
        tags=["Orders"],
    )
    def post(self, request, pk):
        """
        Generate a bill for an order.
        Generates a bill for the specified order.

        """
        order_item = get_object_or_404(OrderItem, id=pk)
        user = request.user

        if user.role == User.Role.CASHIER:
            if order_item.is_paid:
                file_name = "payment.html"
                context = {"order_item": order_item}
                html_content = render_to_string("market/payment_template.html", context)

                with open(file_name, "w") as file:
                    file.write(html_content)

                return Response("Payment is created...", status=status.HTTP_200_OK)
            return Response(
                "The order is not paid.", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            "Only cashiers can generate bills.", status=status.HTTP_403_FORBIDDEN
        )


class ChangeOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="""
            Change the status of an order.
            Changes the status of the specified order.

            Parameters:
                - `pk` (int): The ID of the order.

            Example response:
            {
                "detail": "Order status updated successfully."
            }
        """,
        responses={200: "Order status updated successfully."},
        tags=["Orders"],
        request={
            "application/json": {
                "type": "object",
                "properties": {"status": {"type": "string", "example": "Completed"}},
                "required": ["status"],
            },
        },
    )
    def post(self, request, pk):
        """
        Changes the status of the specified order.
        """
        order_item = get_object_or_404(OrderItem, id=pk)
        user = request.user

        if user.role != User.Role.USER:
            status = request.data.get("status")
            order_item.status = status
            order_item.save()
            return Response(
                {"detail": "Order status updated successfully."},
            )
        return Response(
            {"detail": "Only administrators can change the status of an order."},
        )

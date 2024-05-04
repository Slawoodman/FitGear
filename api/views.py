from rest_framework.permissions import IsAuthenticated, AllowAny  
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import UpdateAPIView
from drf_spectacular.types import OpenApiTypes

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import ProductSerializer, OrderItemSerializer, OrderSerializer, CartSerializer, CartItemSerializer
from market.models import Product, OrderItem, Cart, CartItem, Order
from market.forms import OrderCreatForm
from users.models import User
from .utils import filter_orders_by_role


from drf_spectacular.utils import extend_schema
from rest_framework import status
from users.forms import CustomUserCreationForm
from users.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken


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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]
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


@extend_schema(tags=["Cart"])
class UpdateCartItemAPIView(UpdateAPIView):
    serializer_class = CartItemSerializer

    @extend_schema(
        description="Update the quantity of a product in the user's cart.",
        tags=["Cart"],
        request=extend_schema(
            parameters=[
                OpenApiParameter(
                    name="quantity",
                    type=int,
                    required=True,
                    location=OpenApiParameter.QUERY,
                    description="The new quantity of the product.",
                )
            ]
        ),
    )
    def put(self, request, pk, quantity):
        if not quantity:
            print("Error: Quantity is required.")
            return Response({"error": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
            cart_item.quantity = quantity
            cart_item.price_sum = cart_item.quantity * cart_item.product.price
            cart_item.save()
            total_price = sum([item.price_sum for item in cart_item.cart.items.all()])
            print("Success: Quantity updated successfully.")
            print(f"Total price: {total_price}")
            return Response({"success": True, "total_price": total_price}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            print("Error: Cart item not found or does not belong to the current user")
            return Response({"error": "Cart item not found or does not belong to the current user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromCartAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication to access this view

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

        # Check if the cart item belongs to the authenticated user
        if cart_item.cart.user != request.user:
            return Response({'error': 'You are not authorized to delete this item'}, status=status.HTTP_403_FORBIDDEN)

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
        responses={200: OrderSerializer()},  # Use OrderSerializer instead of OrderItemSerializer
        tags=["Orders"],
    )
    def get(self, request, pk):
        """
        Get an order by ID.
        Returns the details of the specified order.
        """
        order = get_object_or_404(Order, id=pk)  # Retrieve the order from the Order model
        # Check if the user is an admin
        if not request.user.role == User.Role.ADMIN: # Assuming `is_staff` is used to determine admin status
            # If the user is not an admin, ensure they can only access their own orders
            if order.customer != request.user:
                return Response({"detail": "You do not have permission to access this order."}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Assuming IsAuthenticated is imported
    
    @extend_schema(
        description="""
            Create a new order, only User can create one.
            Creates a new order for the specified product.

            Example request body:
                {
                    "address": "U address",
                    "postal_code": "U postal_code",
                    "department_number": "U department_number",
                    "phone": "U phone number",
                }

            Example response:
                "New order created successfully!"
        """,
        responses={201: "New order created successfully!"},
        tags=["Orders"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "address": {"type": "string", "example": "U'r address"},
                    "postal_code": {"type": "string", "example": "U'r postal_code"},
                    "department_number": {"type": "string", "example": "U'r department_number"},
                    "phone": {"type": "string", "example": "U'r phone number"},
                },
                "required": ["address", "postal_code", "department_number", "phone",],
            },
        },
    )
    def post(self, request):
        """
        Create a new order, only User can create one.
        """
        form = OrderCreatForm(request.data)
    
        if form.is_valid():
        # Create a new order
            order = form.save(commit=False)
            order.customer = request.user
            order.save()

        # Get the current user's cart
            cart = Cart.objects.get(user=request.user)

        # Get cart items for the user's cart
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items:
                return Response({"error": "Cannot create an order from an empty cart"}, status=status.HTTP_400_BAD_REQUEST)

        # Add cart items to the order and calculate total price
            total_price = 0
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order_of_item=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price * cart_item.quantity
                )
                total_price += order_item.price

        # Update total price of the order
            order.total_price = total_price
            order.save()

        # Clear the user's cart
            cart_items.delete()

            return Response({"success": "New order created successfully!"}, status=status.HTTP_201_CREATED)
    
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


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
        order = get_object_or_404(Order, id=pk)
        user = request.user
        role = user.role

        if role == User.Role.USER and order.customer == user:
            try:
                order.status_to_pading()
                return Response("Payment successful.", status=status.HTTP_200_OK)
            except:
                return Response(
                    "An error occurred.", status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            "Only owners can pay for the order.", status=status.HTTP_403_FORBIDDEN
        )


class OrderGenBillAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

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
        try:
            order_item = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        context = {"order_item": order_item}
        html_content = render_to_string("market/payment_template.html", context)

        order_item.file.save("payment.html", ContentFile(html_content), save=True)

        serializer = OrderSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                STATUS_CHOICES = (
                    ("Undecided", "UNDECIDED"),
                    ("Paid", "PAID"),
                    ("Completed", "COMPLETED"),
                    )

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
        order_item = get_object_or_404(Order, id=pk)
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


class LoginUserAPIView(APIView):
    @extend_schema(
        operation_id="login_user",
        description="Authenticate a user and obtain access and refresh tokens.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            }
        },
        responses={
            200: {
                "description": "Success",
                "examples": {
                    "Success Example": {
                        "value": {
                            "refresh": "...",
                            "access": "..."
                        },
                        "name": "Success Example"
                    }
                }
            },
            401: {
                "description": "Invalid credentials",
                "examples": {
                    "Invalid Credentials Example": {
                        "value": {
                            "error": "Invalid credentials"
                        },
                        "name": "Invalid Credentials Example"
                    }
                }
            }
        },
    )
    def post(self, request):
        username = request.data.get("username", "").lower()
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterUserAPIView(APIView):
    @extend_schema(
        operation_id="register_user",
        description="Register a new user and obtain access and refresh tokens.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                    "password2": {"type": "string"}
                },
                "required": ["username", "email", "password", "password2"]
            }
        },
        responses={
            201: {
                "description": "User created",
                "examples": {
                    "User Created Example": {
                        "value": {
                            "refresh": "...",
                            "access": "..."
                        },
                        "name": "User Created Example"
                    }
                }
            },
            400: {
                "description": "Bad request",
                "examples": {
                    "Bad Request Example": {
                        "value": {
                            "error": "...",
                            "details": "..."
                        },
                        "name": "Bad Request Example"
                    }
                }
            },
        },
    )
    def post(self, request):
        form = CustomUserCreationForm(request.data)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "An error occurred during registration.", "details": form.errors}, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="logout_user",
        description="Logout a user and invalidate access and refresh tokens.",
        responses={
            200: {
                "description": "User logged out",
                "examples": {
                    "User Logged Out Example": {
                        "value": {
                            "message": "User was logged out."
                        },
                        "name": "User Logged Out Example"
                    }
                }
            },
        },
    )
    def post(self, request):
        logout(request)
        return Response({"message": "User was logged out."}, status=status.HTTP_200_OK)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.http import JsonResponse
import json
from django.core.files.base import ContentFile
from django.views import View
from django.http import HttpResponse
from .models import Product, OrderItem, Cart, CartItem, ProductReview, Order, Category
from .forms import OrderCreatForm, ReviewCreatForm
from .utils import get_choices, filter_orders
import mimetypes
from django.db import transaction


# Class based view to display the main page
class MainPageView(View):
    def get(self, request):
        # Fetch all categories from the database
        categories = Category.objects.all()

        # Initialize the products queryset
        products = Product.objects.all()

        # Check if a category filter is applied
        category_id = request.GET.get('category')
        if category_id:
            # Filter products based on the selected category
            products = products.filter(category_id=category_id)

        # Define context variables that are passed to the template
        context = {"products": products, "categories": categories}

        # Render the 'main.html' template, passing in the context
        return render(request, "market/main.html", context)


class CartView(View):
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_price = sum([item.quantity * item.product.price for item in cart.items.all()])
        form = OrderCreatForm()
        return render(request, 'market/cart.html', {'cart': cart, 'total_price': total_price, 'form': form})

    @transaction.atomic
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_price = sum([item.quantity * item.product.price for item in cart.items.all()])
        form = OrderCreatForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.customer = request.user
                order.total_price = total_price
                order.save()
                for cart_item in cart.items.all():
                    order_item = OrderItem.objects.create(
                        order_of_item=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.price_sum
                    )
                cart.items.all().delete()
            return redirect('showorders')
        return render(request, 'market/cart.html', {'cart': cart, 'total_price': total_price, 'form': form})


class AddToCartView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += int(request.GET['quantity'])
        cart_item.save()
        return redirect('cart')


class UpdateCartItemView(View):
    def post(self, request):
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = data.get('quantity')
        try:
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.quantity = new_quantity
            cart_item.price_sum = cart_item.quantity * cart_item.product.price
            cart_item.save()
            cart = cart_item.cart
            for item in cart.items.all():
                item.price_sum = item.product.price * item.quantity
                item.save()
            total_price = sum([item.price_sum for item in cart.items.all()])
            return JsonResponse({'success': True, 'total_price': total_price})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cart item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class RemoveFromCartView(View):
    def get(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()
        return redirect('cart')


class ProductView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        reviews = ProductReview.objects.filter(product=product)
        form = ReviewCreatForm()
        context = {
            'product': product,
            'reviews': reviews,
            'form': form
        }
        return render(request, 'market/product_page.html', context)

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        form = ReviewCreatForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
        reviews = ProductReview.objects.filter(product=product)
        context = {
            'product': product,
            'reviews': reviews,
            'form': form
        }
        return render(request, 'market/product_page.html', context)


# Class based view to display all orders. It uses the LoginRequiredMixin to ensure that only logged in users can access this view.
class GetOrdersView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It fetches all the order items and renders the order list page.
    def get(self, request):
        # Fetch all OrderItem objects from the database
        data = Order.objects.all()

        # Filter the orders based on the current request
        orders = filter_orders(request, data)

        # Define context variables that are passed to the template.
        context = {"orders": orders}

        # Render the 'order_list.html' template, passing in the context.
        return render(request, "market/order_list.html", context)


# Class based view to create a user order. It also uses the LoginRequiredMixin.
class CreateUserOrderView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It renders the order creation form.
    def get(self, request, pk):
        # Fetch the product with the provided primary key (pk)
        item = Product.objects.get(id=pk)

        # Initialize the order creation form
        form = OrderCreatForm()

        # Define context variables that are passed to the template.
        context = {"form": form}

        # Render the 'order_form.html' template, passing in the context
        return render(request, "market/order_form.html", context)

    # Function to handle HTTP POST requests. It performs the order creation operation.
    def post(self, request, pk):
        # Fetch the product with the provided primary key (pk)
        item = Product.objects.get(id=pk)

        # Initialize the order creation form with the data received from the user
        form = OrderCreatForm(request.POST)

        # Check if the form data is valid
        if form.is_valid():
            # If the form data is valid, create a new order instance but don't save it to the database yet.
            order = form.save(commit=False)

            # Assign the product and customer to the order
            order.product = item
            order.customer = request.user

            # Now save the order instance into the database.
            order.save()

            # Redirect to the 'showorders' page.
            return redirect("showorders")

        context = {"form": form}
        # If the form data was not valid, re-render the order form with the form errors.
        return render(request, "market/order_form.html", context)


# Class based view to mark an order item as paid. It also uses the LoginRequiredMixin.
class MarkOrderItemAsPaidView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It marks the order item as paid and redirects to the orders page.
    def get(self, request, pk):
        # Fetch the OrderItem with the provided primary key (pk) or return 404 if it doesn't exist
        order_item = get_object_or_404(Order, id=pk)

        # Mark the order item as paid
        order_item.status_to_pading()

        # Redirect to the 'showorders' page.
        return redirect("showorders")


# Class based view to change the status of an order. It also uses the LoginRequiredMixin.
class ChangeOrderStatusView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It displays the form to change the status of an order.
    def get(self, request, pk):
        # Fetch the OrderItem with the provided primary key (pk) or return 404 if it doesn't exist
        order = get_object_or_404(Order, id=pk)

        # Get the status choices for the current order
        choices = get_choices(request, order)

        # Define context variables that are passed to the template.
        context = {"order": order, "page": "edit", "choices": choices}

        # Render the 'order_form.html' template, passing in the context.
        return render(request, "market/order_form.html", context)

    # Function to handle HTTP POST requests. It performs the operation of changing the status of an order.
    def post(self, request, pk):
        # Fetch the OrderItem with the provided primary key (pk) or return 404 if it doesn't exist
        order = get_object_or_404(Order, id=pk)

        # Get the status choices for the current order
        choices = get_choices(request, order)

        # Get the status from the POST data
        status = request.POST.get("status")

        # Check if the status is a valid choice
        if status in dict(Order.STATUS_CHOICES):
            # If it's a valid status, change the status of the order and save it
            order.status = status
            order.save()

            # Redirect to the 'showorders' page.
            return redirect("showorders")
        else:
            # If it's not a valid status, return an error message
            return HttpResponse("Wrong value")


# Class based view to generate a payment HTML file. It also uses the LoginRequiredMixin.
class GeneratePaymentHtmlView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It generates a payment HTML file and redirects to the orders page.
    def get(self, request, pk):
        # Fetch the OrderItem with the provided primary key (pk)
        order_item = Order.objects.get(id=pk)

        # The filename for the payment HTML file
        file_name = "payment.html"

        # Define context variables that are passed to the template.
        context = {"order_item": order_item}

        # Render the payment template as a string
        html_content = render_to_string("market/payment_template.html", context)

        # Save the generated HTML content as a file in the order item
        order_item.file.save(file_name, ContentFile(html_content), save=True)

        # Redirect to the 'showorders' page.
        return redirect("showorders")


# Class based view to download a file. It also uses the LoginRequiredMixin.
class DownloadFileView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It returns the requested file for download.
    def get(self, request, pk):
        # Fetch the OrderItem with the provided primary key (pk)
        order_item = Order.objects.get(id=pk)

        # Get the file extension of the order item's file
        file_extension = order_item.file.name.split(".")[-1]

        # Guess the content type of the file based on its extension
        content_type, _ = mimetypes.guess_type(file_extension)

        # Create a HttpResponse with the order item's file and the guessed content type
        response = HttpResponse(order_item.file, content_type=content_type)

        # Set the 'Content-Disposition' header to suggest a filename to the browser
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{order_item.file.name}"'

        # Return the response
        return response

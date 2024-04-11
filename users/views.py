# Import necessary modules and libraries. These are building blocks for creating views and handling HTTP requests/responses.
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import User


# Class based view to handle user login
class LoginUserView(View):
    # Function to handle HTTP GET requests. It renders the login page.
    def get(self, request):
        # Set the page variable to 'login'
        page = "login"

        # Check if the user is already authenticated (logged in). If so, they are redirected to the 'main' page.
        if request.user.is_authenticated:
            return redirect("main")

        # Define context variables that are passed to the template.
        context = {"page": page}

        # Render the 'login_reg.html' template, passing in the context
        return render(request, "users/login_reg.html", context)

    # Function to handle HTTP POST requests. It performs the login operation.
    def post(self, request):
        # Set the page variable to 'login'
        page = "login"

        # If the user is already authenticated (logged in), redirect them to the main page.
        if request.user.is_authenticated:
            return redirect("main")

        # Extract username and password from the POST data (data sent by the user via form submission).
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        # Attempt to fetch the User object that has the provided username. If no such User exists, display an error message.
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Username does not exist")
            context = {"page": page}
            return render(request, "users/login_reg.html", context)

        # Use Django's built-in authentication system to verify the provided username and password.
        user = authenticate(request, username=username, password=password)

        # If the user was successfully authenticated, log them in and redirect to the 'next' page (or 'main' if no 'next' is specified)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "main"))
        else:
            # If authentication failed, display an error message.
            messages.error(request, "Username or password is incorrect")
            context = {"page": page}
            return render(request, "users/login_reg.html", context)


# Class based view to handle user registration
class RegisterUserView(View):
    # Function to handle HTTP GET requests. It renders the user registration page.
    def get(self, request):
        # Set the page variable to 'register'
        page = "register"

        # Initialize the form for user registration.
        form = CustomUserCreationForm()

        # Define context variables that are passed to the template.
        context = {"page": page, "form": form}

        # Render the 'login_reg.html' template, passing in the context.
        return render(request, "users/login_reg.html", context)

    # Function to handle HTTP POST requests. It performs the user registration operation.
    def post(self, request):
        # Set the page variable to 'register'
        page = "register"

        # Initialize the registration form with the data received from the user.
        form = CustomUserCreationForm(request.POST)

        # Check if the form data is valid.
        if form.is_valid():
            # If the form data is valid, create a new user instance but don't save it to the database yet.
            user = form.save(commit=False)

            # Convert the username to lowercase.
            user.username = user.username.lower()

            # Now save the user instance into the database.
            user.save()

            # Display a success message.
            messages.success(request, "User account was successfully created")

            # Log the user in and redirect to the 'main' page.
            login(request, user)
            return redirect("main")
        else:
            # If the form data was not valid, display an error message.
            messages.error(request, "An error occurred during registration")

        context = {"page": page, "form": form}
        # Re-render the registration page with the form errors.
        return render(request, "users/login_reg.html", context)


# Class based view to handle user logout
class LogoutUserView(LoginRequiredMixin, View):
    # Function to handle HTTP GET requests. It performs the logout operation.
    def get(self, request):
        # Log out the user.
        logout(request)

        # Display a success message.
        messages.success(request, "User was logged out")

        # Redirect to the 'main' page.
        return redirect("main")

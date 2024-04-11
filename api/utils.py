from users.models import User
from market.models import OrderItem


def filter_orders_by_role(user):
    role = user.role

    print(role)
    if role == User.Role.USER:
        return OrderItem.objects.filter(customer=user)

    elif role == User.Role.CASHIER:
        return OrderItem.objects.filter(status__in=["Undecided", "Paid"])

    elif role == User.Role.CONSULTANT:
        return OrderItem.objects.filter(status__in=["Paid", "Completed"])

    elif role == User.Role.BOOKER:
        return OrderItem.objects.all()

    # Return an empty queryset for unknown roles
    return OrderItem.objects.none()

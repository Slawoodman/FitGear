from users.models import User
from market.models import Order


def filter_orders_by_role(user):
    role = user.role

    print(role)
    if role == User.Role.USER:
        return Order.objects.filter(customer=user)


    elif role == User.Role.ADMIN:
        return Order.objects.all()

    # Return an empty queryset for unknown roles
    return Order.objects.none()
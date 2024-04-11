from django.db.models import Q


def get_choices(request, order):
    role = request.user.role
    if role == "CASHIER":
        choices = order.STATUS_CHOICES[:2]
    elif role == "CONSULTANT":
        choices = [order.STATUS_CHOICES[2]]
    else:
        choices = order.STATUS_CHOICES
    return choices


def filter_orders(request, queryset):
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    status = request.GET.get("status")

    # Base queryset

    # Apply filters
    if from_date and to_date:
        queryset = queryset.filter(created__range=[from_date, to_date])

    if status:
        queryset = queryset.filter(status=status)

    # Additional role-based filtering
    user_role = request.user.role
    q = Q()

    if user_role == "CASHIER":
        q |= Q(status__in=["Undecided", "Paid"])
    elif user_role == "CONSULTANT":
        q |= Q(status__in=["Paid", "Completed"])
    elif user_role == "USER":
        q |= Q(customer=request.user)

    orders = queryset.filter(q)

    # Order the queryset
    orders = orders.order_by("created", "status")
    return orders

from django.db.models import Sum, Count, F
from orders.models import Order, OrderItem
from users.models import User
from catalog.models import Bouquet


def get_revenue(start_date, end_date):
    return Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0


def get_profit(start_date, end_date):
    revenue = get_revenue(start_date, end_date)
    cost = OrderItem.objects.filter(
        order__created_at__gte=start_date,
        order__created_at__lte=end_date
    ).aggregate(total_cost=Sum(F('bouquet__cost_price') * F('quantity')))['total_cost'] or 0
    return revenue - cost


def get_order_count(start_date, end_date):
    return Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).count()


def get_bouquets_sold(start_date, end_date):
    return OrderItem.objects.filter(
        order__created_at__gte=start_date,
        order__created_at__lte=end_date
    ).aggregate(total_bouquets=Sum('quantity'))['total_bouquets'] or 0


def get_top_users(start_date, end_date):
    return User.objects.filter(
        orders__created_at__gte=start_date,
        orders__created_at__lte=end_date
    ).annotate(order_count=Count('orders')).order_by('-order_count')[:5]


def get_top_bouquets(start_date, end_date):
    return Bouquet.objects.filter(
        orderitem__order__created_at__gte=start_date,
        orderitem__order__created_at__lte=end_date
    ).annotate(total_sold=Sum('orderitem__quantity')).order_by('-total_sold')[:5]

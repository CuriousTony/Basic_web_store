from django import template
from ..models import Review

register = template.Library()


@register.filter
def has_review(bouquet, order):
    return Review.objects.filter(
        bouquet=bouquet,
        user=order.user,
        order=order
    ).exists()

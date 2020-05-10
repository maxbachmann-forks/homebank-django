from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def percentage_of(value, total_value):
    if total_value == Decimal("0"):
        return 0
    return Decimal(value) / Decimal(total_value) * 100

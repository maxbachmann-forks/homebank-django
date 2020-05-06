from django import template
from decimal import Decimal
from babel.numbers import format_currency
from unicodedata import normalize

register = template.Library()


@register.filter
def absolute_price(number_str):
    price = abs(Decimal(number_str))
    return normalize('NFKD', format_currency(price, 'EUR', locale='nl_NL'))

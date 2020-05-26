from decimal import Decimal
from unicodedata import normalize

from babel.numbers import format_currency
from django import template

register = template.Library()


@register.filter
def absolute_price(number_str):
    price = 0

    if number_str != '':
        price = abs(Decimal(number_str))

    return normalize('NFKD', format_currency(price, 'EUR', locale='nl_NL'))

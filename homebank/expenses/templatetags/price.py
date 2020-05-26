from decimal import Decimal
from unicodedata import normalize

from babel.numbers import format_currency
from django import template

register = template.Library()


@register.filter
def price(number_str):
    return normalize('NFKD', format_currency(Decimal(number_str), 'EUR', locale='nl_NL'))

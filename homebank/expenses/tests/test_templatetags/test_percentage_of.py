from decimal import Decimal

from homebank.expenses.templatetags.percentage_of import percentage_of


def test_percentage_of_whole():
    result = percentage_of("10.50", "1050.00")

    assert result == 1


def test_full_percentage():
    result = percentage_of("1", "1")

    assert result == 100


def test_zero_devision():
    result = percentage_of("1", Decimal("0"))

    assert result == 0

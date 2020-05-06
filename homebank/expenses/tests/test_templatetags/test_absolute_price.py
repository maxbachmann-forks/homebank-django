from homebank.expenses.templatetags.absolute_price import absolute_price


def test_formats_to_euro():
    result = absolute_price("10.00");

    assert result == "€ 10,00"


def test_formats_negative_price_to_positive_currency():
    result = absolute_price("-20.50");

    assert result == "€ 20,50"


def test_formats_simple_integer_to_decimal_price():
    result = absolute_price("20");

    assert result == "€ 20,00"

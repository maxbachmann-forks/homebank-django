from decimal import Decimal

import pytest
from datetime import date
from django.http import HttpResponse
from pytest_django.asserts import assertContains, assertRedirects
from django.urls import reverse
from django.test import Client, RequestFactory
from testfixtures import Replace, test_datetime

from homebank.users.models import User
from ..views import (
    RedirectToMonthView,
    MonthView
)
from ...transaction_management.tests.factories import TransactionFactory, CategoryFactory

pytestmark = pytest.mark.django_db


def test_redirects_to_previous_month(rf, user: User):
    with Replace('homebank.expenses.views.datetime', test_datetime(2020, 3, 1)):
        request = rf.get(reverse("expenses:home"))
        request.user = user
        response = RedirectToMonthView.as_view()(request)
        response.client = Client()

        expected_month_str = f"2020-02"

        assertRedirects(response, reverse("expenses:month", kwargs={'date': expected_month_str}),
                        target_status_code=302)


def test_can_navigate_to_neighbouring_months(rf, user: User):
    response = _navigate_to_month(rf, user, "2020-04")
    assertContains(response, f'href="{reverse("expenses:month", kwargs={"date": "2020-03"})}"')
    assertContains(response, f'href="{reverse("expenses:month", kwargs={"date": "2020-05"})}"')


def test_shows_total_income(rf, user: User):
    category = CategoryFactory(name='Budget')
    for i in range(0, 3):
        TransactionFactory(date=date(2020, 4, 1), user=user, category=category, inflow=50)

    TransactionFactory(date=date(2020, 3, 1), user=user, category=category, inflow=50)
    response = _navigate_to_month(rf, user, "2020-04")

    assertContains(response, '€ 150,00')


def test_shows_total_savings(rf, user: User):
    category = CategoryFactory(name='Sparen')
    for i in range(0, 3):
        TransactionFactory(date=date(2020, 4, 1), user=user, category=category, outflow=50, inflow=0)

    TransactionFactory(date=date(2020, 3, 1), user=user, category=category, outflow=50, inflow=0)
    response = _navigate_to_month(rf, user, "2020-04")

    assertContains(response, '€ 150,00')

def test_shows_total_expenses(rf, user: User):
    category_savings = CategoryFactory(name='Sparen')
    category_income = CategoryFactory(name='Budget')
    category_expenses = CategoryFactory(name='Uitgaven')
    for i in range(0, 3):
        TransactionFactory(date=date(2020, 4, 1), user=user, category=category_expenses, outflow=50, inflow=0)

    TransactionFactory(date=date(2020, 4, 1), user=user, category=category_savings, outflow=44, inflow=0)
    TransactionFactory(date=date(2020, 4, 1), user=user, category=category_income, outflow=0, inflow=66)
    response = _navigate_to_month(rf, user, "2020-04")

    assertContains(response, '€ 150,00')
    assertContains(response, '€ 44,00')
    assertContains(response, '€ 66,00')


def _navigate_to_month(rf: RequestFactory, user: User, month_str: str) -> HttpResponse:
    request_kwargs = {"date": "2020-04"}
    url = reverse("expenses:month", kwargs=request_kwargs)
    request = rf.get(url)
    request.user = user
    return MonthView.as_view()(request, **request_kwargs)

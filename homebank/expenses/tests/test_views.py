import pytest
from pytest_django.asserts import assertContains, assertRedirects
from django.urls import reverse
from django.test import Client
from datetime import datetime
from testfixtures import Replace, test_datetime

from homebank.users.models import User
from ..views import (
    RedirectToMonthView,
    MonthView
)

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
    request_kwargs = {"date": "2020-04"}
    url = reverse("expenses:month", kwargs=request_kwargs)
    request = rf.get(url)
    request.user = user
    response = MonthView.as_view()(request, **request_kwargs)

    assertContains(response, f'href="{reverse("expenses:month", kwargs={"date": "2020-03"})}"')
    assertContains(response, f'href="{reverse("expenses:month", kwargs={"date": "2020-05"})}"')

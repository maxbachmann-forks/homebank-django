# when visiting the expenses page
# I can see a sum of expenses per category
# and behind those an average of the past year
import pytest
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal

from django.test.client import Client
from django.core.management import call_command

from homebank.transaction_management.models import Category, Transaction
from homebank.users.models import User
from homebank.expenses.models import MonthlyExpenseSummary


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def load_data(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', Path(__file__).parent / "./fixtures/users.yml")
        call_command('loaddata', Path(__file__).parent / "./fixtures/transaction_management_small")


@pytest.fixture()
def february_overview():
    user = User.objects.get(username='admin')
    month = datetime(2020, 2, 1)
    return Category.objects.overview_for_month(month, user)


def test_query_results(february_overview):
    mortgage = next(summary for summary in february_overview if summary.category_id == 1)
    house = next(summary for summary in february_overview if summary.category_id == 2)
    empty = next(summary for summary in february_overview if summary.category_id == 3)

    assert len(february_overview) == len(Category.objects.all())
    assert mortgage.sum_outflow == Decimal("911.11")
    assert mortgage.sum_inflow == 0
    assert mortgage.total_outflow == Decimal("1822.22")
    assert mortgage.total_inflow == 0
    assert mortgage.min_transaction_date == date(2020, 1, 4)
    assert mortgage.max_transaction_date == date(2020, 2, 4)

    assert house.sum_outflow == Decimal("10")
    assert house.sum_inflow == 0
    assert house.total_outflow == Decimal("30")
    assert house.total_inflow == 0
    assert house.min_transaction_date == date(2019, 12, 29)
    assert house.max_transaction_date == date(2020, 2, 2)

    assert empty.sum_outflow == 0
    assert empty.sum_inflow == 0
    assert empty.total_outflow == 0
    assert empty.total_inflow == 0
    assert empty.min_transaction_date is None
    assert empty.max_transaction_date is None


def test_calculates_averages_from_query_results(february_overview: MonthlyExpenseSummary):
    mortgage = next(summary for summary in february_overview if summary.category_id == 1)
    house = next(summary for summary in february_overview if summary.category_id == 2)
    empty = next(summary for summary in february_overview if summary.category_id == 3)
    free_time = next(summary for summary in february_overview if summary.category_id == 6)

    # Asserts from computed
    assert mortgage.average_monthly_outflow == Decimal("911.11")
    assert mortgage.balance_of_month == Decimal("-911.11")
    assert mortgage.average_monthly_balance == Decimal("-911.11")
    # note there's no january outflow for "house", but it needs to be included!
    assert house.average_monthly_outflow == Decimal("10")
    assert empty.average_monthly_outflow == 0
    assert empty.average_monthly_inflow == 0

    assert free_time.balance_of_month == Decimal("-33.50")
    assert free_time.average_monthly_outflow == Decimal("34.25")
    assert free_time.average_monthly_inflow == Decimal("22.5")
    assert free_time.average_monthly_balance == Decimal("-11.75")

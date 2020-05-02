# when visiting the expenses page
# I can see a sum of expenses per category
# and behind those an average of the past year
from datetime import datetime, date
import pytest
from pathlib import Path
from homebank.utils import path_for
from homebank.transaction_management.models import Category, Transaction
from homebank.users.models import User
from django.test.client import Client

from django.core.management import call_command
from decimal import Decimal


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
    mortgage = next(category for category in february_overview if category.id == 1)
    house = next(category for category in february_overview if category.id == 2)

    # Asserts from the query

    assert len(february_overview) == len(Category.objects.all())
    assert mortgage.sum_outflow == Decimal("911.11")
    assert mortgage.sum_inflow is None
    assert mortgage.total_outflow == Decimal("1822.22")
    assert mortgage.total_inflow == None
    assert mortgage.min_date == date(2020, 1, 4)
    assert mortgage.max_date == date(2020, 2, 4)

    assert house.sum_outflow == Decimal("10")
    assert house.sum_inflow is None
    assert house.total_outflow == Decimal("30")
    assert house.total_inflow == None
    assert house.min_date == date(2019, 12, 29)
    assert house.max_date == date(2020, 2, 2)

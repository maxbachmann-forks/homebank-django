from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import RequestFactory

from homebank.users.models import User
from homebank.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def load_fixture_data(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', Path(__file__).parent / "./expenses/tests/fixtures/users.yml")
        call_command('loaddata', Path(__file__).parent / "./expenses/tests/fixtures/transaction_management_small")

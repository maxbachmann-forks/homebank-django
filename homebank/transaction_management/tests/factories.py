from datetime import datetime

from factory import DjangoModelFactory, Faker, fuzzy, SubFactory

from homebank.users.tests.factories import UserFactory
from ..models import Transaction, Category

this_year = datetime.now()


class CategoryFactory(DjangoModelFactory):
    name = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText(length=40)

    class Meta:
        model = Category


class TransactionFactory(DjangoModelFactory):
    code = Faker('md5')
    to_account_number = Faker('iban')
    date = fuzzy.FuzzyDate(datetime(this_year.year, 1, 1), datetime(this_year.year, 12, 1))
    payee = Faker('first_name')
    memo = fuzzy.FuzzyText()
    outflow = fuzzy.FuzzyDecimal(1, 100)
    inflow = fuzzy.FuzzyDecimal(1, 100)
    user = SubFactory(UserFactory)
    category = SubFactory(CategoryFactory)

    class Meta:
        model = Transaction

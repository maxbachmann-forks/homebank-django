import pytest

from homebank.transaction_management.migrations.utils import seed_categories
from homebank.transaction_management.models import Category

pytestmark = pytest.mark.django_db


class MigrationApp:

    def get_model(self, app, model_name):
        return Category


@pytest.fixture(autouse=True)
def clean_categories():
    categories = Category.objects.all()
    [category.delete() for category in categories]


def test_category_seed():
    apps = MigrationApp()
    seed_categories(apps, None)

    category = Category.objects.get(name='Hypotheek')
    assert category is not None
    assert category.description == 'Vaste lasten voor je huis'

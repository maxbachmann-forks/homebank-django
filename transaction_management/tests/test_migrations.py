import pytest

from transaction_management.models import Category
from transaction_management.migrations.utils import seed_categories

pytestmark = pytest.mark.django_db


class MigrationApp:
    def get_model(self, app, model_name):
        return Category


@pytest.fixture(autouse=True)
def clean_categories():
    categories = Category.objects.all()
    for category in categories:
        category.delete()


def test_category_seed():
    apps = MigrationApp()
    seed_categories(apps, None)

    category = Category.objects.get(name='Hypotheek')
    assert category is not None
    assert category.description == 'Vaste lasten voor je huis'

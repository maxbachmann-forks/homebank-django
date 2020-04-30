import pytest

from django.contrib.messages import get_messages
from homebank.users.models import User

from homebank.transaction_management.tests.utils import open_file


class TestTransactionAdmin:
    # @pytest.fixture(autouse=True)
    # def user(self) -> None:
    #     user = User.objects.create_superuser(username='test', password='test')
    #     self.client.force_login(user)

    def test_can_go_to_overview(self, admin_client):
        response = admin_client.get('/admin/transaction_management/transaction/')
        assert response.status_code == 200
        assert 'href="import-csv/"' in str(response.content)

    def test_shows_csv_import(self, admin_client):
        response = admin_client.get('/admin/transaction_management/transaction/import-csv/')
        assert response.status_code == 200
        assert 'admin/transaction_management/csv_form.html' in (t.name for t in response.templates)

    def test_upload_csv(self, admin_client):
        file = open_file('./data/single_dummy.csv')
        file_form = {'csv_file': file, 'name': 'Timo'}
        response = admin_client.post('/admin/transaction_management/transaction/import-csv/', data=file_form)
        assert response.status_code == 302

    def test_upload_invalid_file(self, admin_client):
        file = open_file('./data/invalid_file.png', 'rb')
        file_form = {'csv_file': file, 'name': 'Invalid'}
        response = admin_client.post('/admin/transaction_management/transaction/import-csv/', data=file_form)
        assert response.status_code == 200
        assert not response.context['form'].is_valid()
        assert 'Files of type image/png are not supported.' in str(response.content)

    def test_show_upload_result(self, admin_client):
        file = open_file('./data/bad-dummy.csv')
        file_form = {'csv_file': file, 'name': 'Timo'}
        response = admin_client.post('/admin/transaction_management/transaction/import-csv/', data=file_form)
        assert response.status_code == 302

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == 'Import result: 1 successful, 1 duplicate(s), 2 failed'

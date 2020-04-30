import pytest

from transaction_management.managers import RabobankCsvRowParser
from transaction_management.models import Transaction
from datetime import date

from homebank.users.models import User


class TestTransactionManager:
    def test_retrieves_only_own_transactions(self):
        user = User.objects.create_superuser('test 1')

        transaction = Transaction.objects.create(
            date=date(2020, 4, 20),
            to_account_number='NL11RABO0101010444',
            payee='timo',
            memo='small memo',
            inflow=10.5,
            user=user
        )

        assert transaction.user == user

        user_2 = User.objects.create_superuser('test 2')

        assert len(user_2.transactions.all()) == 0
        assert len(Transaction.objects.for_user(user_2)) == 0


@pytest.fixture
def parser():
    return RabobankCsvRowParser()


class TestRabobankCsvRowParser:
    def test_parses_inflow_transaction(self, parser):
        user = User.objects.create_user("timo")
        csv_row = ['NL11RABO0104955555', 'EUR', 'RABONL2U', '000000000000007213', '2019-09-01', '2019-09-01', '+2,50',
                   '+1868,12', 'NL42RABO0114164838', 'J.M.G. Kerkhoffs eo', '', '', 'RABONL2U', 'cb', '', '', '', '',
                   '', 'Spotify', ' ', '', '', '', '', '']

        transaction = parser.parse(csv_row)
        transaction.user = user

        transaction.full_clean()
        transaction.save()

    def test_generates_an_unique_identifier_based_on_the_row_values(self, parser):
        csv_row = ['NL11RABO0104955555', 'EUR', 'RABONL2U', '000000000000007213', '2019-09-01', '2019-09-01', '+2,50',
                   '+1868,12', 'NL42RABO0114164838', 'J.M.G. Kerkhoffs eo', '', '', 'RABONL2U', 'cb', '', '', '', '',
                   '', 'Spotify', ' ', '', '', '', '', '']

        transaction = parser.parse(csv_row)

        assert '6a25f09148bead1f64212179d61f9c37' == transaction.code

    def test_fails_parser_an_invalid_row(self, parser):
        csv_row = [0, 0, 0, 0, None]

        with pytest.raises(IndexError):
            parser.parse(csv_row)

    def test_incasso_id_get_appended_to_memo(self, parser):
        csv_row = ['NL11RABO0104955555', 'EUR', 'RABONL2U', '000000000000007213', '2019-09-01', '2019-09-01', '-2,50',
                   '+1868,12', 'NL42RABO0114164838', 'J.M.G. Kerkhoffs eo', '', '', 'RABONL2U', 'cb', '', '',
                   'abc-def-ghi', '', '', 'Sport abo', ' ', '', '', '', '', '']  # rubocop:disable Layout/LineLength

        transaction = parser.parse(csv_row)

        assert 'Sport abo (Incasso: abc-def-ghi)' == transaction.memo

import csv
from datetime import datetime, date
from decimal import InvalidOperation, Decimal
from typing import List

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Min, Q, Sum

from homebank.expenses.models import MonthlyExpenseSummary
from homebank.users.models import User
from .utils import create_unique_code


class FileParseResult:
    def __init__(self):
        self.amount_successful = 0
        self.amount_duplicate = 0
        self.amount_faulty = 0


class TransactionManager(models.Manager):
    def _query_set(self):
        return super(TransactionManager, self).get_queryset()

    def for_user(self, user):
        return self._query_set().filter(user=user)

    def for_user_expenses(self, user):
        return self.for_user(user).exclude(category__name__in=['Budget', 'Sparen'])

    def total_budget_for_month(self, month: date, user: User) -> float:
        return \
        self.for_user(user).filter(category__name='Budget', date__year=month.year, date__month=month.month).aggregate(
            Sum('inflow'))['inflow__sum'] or 0

    def total_spent_for_month(self, month: date, user: User):
        query_set = self.for_user_expenses(user)
        result = query_set.filter(
            date__year=month.year, date__month=month.month, category__isnull=False
        ).aggregate(
            total_outflow=Sum('outflow'), total_inflow=Sum('inflow')
        )

        return Decimal(result['total_inflow'] or 0) - Decimal(result['total_outflow'] or 0)

    def create_from_file(self, file_stream, user) -> FileParseResult:
        result = FileParseResult()
        parser = RabobankCsvRowParser()
        csv_reader = csv.reader(file_stream, delimiter=',', quotechar='"')
        next(csv_reader)  # skip header

        for row in csv_reader:
            self._process_row(row, result, parser, user)

        return result

    def _process_row(self, row, result, parser, user):
        try:
            transaction = parser.parse(row)
            transaction.user = user
            transaction.full_clean()
            transaction.save()
            result.amount_successful += 1
        except ValidationError as error:
            if 'code' in error.message_dict:
                result.amount_duplicate += 1
            else:
                result.amount_faulty += 1
        except (InvalidOperation, IndexError, ValueError):
            result.amount_faulty += 1


class CategoryManager(models.Manager):
    def overview_for_month(self, month: date, user: User) -> List[MonthlyExpenseSummary]:
        month_subquery = Q(transactions__date__year=month.year,
                           transactions__date__month=month.month, transactions__user__id=user.id)
        total_subquery = Q(transactions__user__id=user.id)

        query_set = super(CategoryManager, self).get_queryset()

        query_result = query_set.exclude(
            name='Budget'
        ).annotate(
            sum_outflow=Sum("transactions__outflow", filter=month_subquery),
            sum_inflow=Sum("transactions__inflow", filter=month_subquery),
            min_date=Min("transactions__date", filter=total_subquery),
            max_date=Max("transactions__date", filter=total_subquery),
            total_outflow=Sum("transactions__outflow", filter=total_subquery),
            total_inflow=Sum("transactions__inflow", filter=total_subquery)
        )

        return [MonthlyExpenseSummary(month, category) for category in query_result]


class RabobankCsvRowParser:
    to_account_number_index = 0
    date_index = 4
    amount_index = 6
    payee_index = 9
    memo_index = 19
    automatic_incasso_id_index = 16
    positive_amount_character = '+'

    def parse(self, row: list):
        from homebank.transaction_management.models import Transaction

        amount_str = self._get_amount_str(row)
        is_positive_amount = amount_str[0] == self.positive_amount_character
        amount = Decimal(amount_str[1:])
        transaction = Transaction(
            to_account_number=row[self.to_account_number_index],
            date=datetime.strptime(row[self.date_index], '%Y-%m-%d'),
            payee=row[self.payee_index],
            memo=self._parse_memo_text_from(row),
            inflow=self._parse_inflow_from(amount, is_positive_amount),
            outflow=self._parse_outflow_from(amount, is_positive_amount),
        )

        transaction.code = create_unique_code(transaction)
        return transaction

    def _get_amount_str(self, row):
        return row[self.amount_index].replace(',', '.')

    def _parse_memo_text_from(self, row) -> str:
        memo = row[self.memo_index]
        incasso_id = row[self.automatic_incasso_id_index]
        incasso_text = '' if not incasso_id.strip(
        ) else f" (Incasso: {incasso_id})"

        return f"{memo}{incasso_text}"

    def _parse_inflow_from(self, amount, is_positive_amount):
        return amount if is_positive_amount else None

    def _parse_outflow_from(self, amount, is_positive_amount):
        return amount if not is_positive_amount else None

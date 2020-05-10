from datetime import datetime
from decimal import Decimal


class MonthlyExpenseSummary():
    def __init__(self, date_of_month: datetime, category):
        self.category_id = category.id
        self.name = category.name
        self.description = category.description
        self.date_of_month = date_of_month
        self.sum_outflow = category.sum_outflow or 0
        self.sum_inflow = category.sum_inflow or 0
        self.min_transaction_date = category.min_date
        self.max_transaction_date = category.max_date
        self.total_outflow = category.total_outflow or 0
        self.total_inflow = category.total_inflow or 0

    @property
    def balance_of_month(self):
        return self.sum_inflow - self.sum_outflow

    @property
    def average_monthly_balance(self):
        return self.average_monthly_inflow - self.average_monthly_outflow

    @property
    def average_monthly_outflow(self):
        if self._amount_of_months is None:
            return 0

        return Decimal(self.total_outflow / self._amount_of_months)

    @property
    def average_monthly_inflow(self):
        if self._amount_of_months is None:
            return 0

        return Decimal(self.total_inflow / self._amount_of_months)

    @property
    def _amount_of_months(self):
        """Get the amount of months between dates, including the starting month

        Returns:
            int -- months between dates
        """
        if self.max_transaction_date is None:
            return None

        return (self.max_transaction_date.year - self.min_transaction_date.year) * 12 + self.max_transaction_date.month - self.min_transaction_date.month + 1

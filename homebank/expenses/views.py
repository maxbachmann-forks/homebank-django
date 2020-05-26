from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView

from homebank.transaction_management.models import Category, Transaction


class RedirectToMonthView(LoginRequiredMixin, RedirectView):  # TODO: I know this needs to be a normal TemplateView
    def get_redirect_url(self, *args, **kwargs):
        previous_month = datetime.now() - relativedelta(months=1)
        return reverse('expenses:month', kwargs={'date': previous_month.strftime('%Y-%m')})


class MonthView(LoginRequiredMixin, TemplateView):
    template_name = "expenses/month.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = kwargs.get('date')
        date = datetime.strptime(date_str, '%Y-%m')
        user = self.request.user

        expenses_per_category = Category.objects.overview_for_month(date, user)
        total_income = Transaction.objects.total_budget_for_month(date, user)
        total_spent = Transaction.objects.total_spent_for_month(date, user)
        total_balans = total_income + total_spent
        savings = self._get_savings_from_overview(expenses_per_category)

        context['date_previous'] = self._get_date_with_month_offset(date, -1)
        context['date_next'] = self._get_date_with_month_offset(date, 1)
        context['date'] = date_str
        context['total_income'] = total_income
        context['total_spent'] = total_spent
        context['expenses_per_category'] = expenses_per_category
        context['total_balans'] = total_balans
        context['total_savings'] = savings - total_balans
        context['savings'] = savings * -1

        return context

    def _get_date_with_month_offset(self, date: datetime, date_offset: int) -> str:
        return self._date_to_month_str(date + relativedelta(months=date_offset))

    def _date_to_month_str(self, date: datetime) -> str:
        return datetime.strftime(date, '%Y-%m')

    def _get_savings_from_overview(self, expenses_per_category):
        try:
            savings = next(
                summary for summary in expenses_per_category if summary.category.name == 'Sparen').balance_of_month
        except StopIteration:
            savings = 0

        return savings

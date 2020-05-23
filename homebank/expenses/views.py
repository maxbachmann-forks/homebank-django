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

        context['date_previous'] = self._get_date_with_month_offset(date, -1)
        context['date_next'] = self._get_date_with_month_offset(date, 1)
        context['date'] = date_str
        context['total_spent'] = Transaction.objects.total_spent_for_month(date, user)
        context['expenses_per_category'] = Category.objects.overview_for_month(date, user)

        return context

    def _get_date_with_month_offset(self, date: datetime, date_offset: int) -> str:
        return self._date_to_month_str(date + relativedelta(months=date_offset))

    def _date_to_month_str(self, date: datetime) -> str:
        return datetime.strftime(date, '%Y-%m')

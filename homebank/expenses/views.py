from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from datetime import datetime

from homebank.transaction_management.models import Category, Transaction
from homebank.expenses.models import MonthlyExpenseSummary


class MonthlyExpensesListView(LoginRequiredMixin, ListView):  # TODO: I know this needs to be a normal TemplateView
    def get_template_names(self):
        return ['expenses/expenses-list.html']

    def get_queryset(self):
        today = datetime(2020, 2, 1)
        queryset = Category.objects.overview_for_month(today, self.request.user)
        print(queryset)
        return queryset


class MonthView(LoginRequiredMixin, TemplateView):
    template_name = "expenses/month.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = kwargs.get('date')
        date = datetime.strptime(date_str, '%Y-%m')
        user = self.request.user

        context['date'] = date_str
        context['total_spent'] = Transaction.objects.total_spent_for_month(date, user)
        context['expenses_per_category'] = Category.objects.overview_for_month(date, user)

        return context

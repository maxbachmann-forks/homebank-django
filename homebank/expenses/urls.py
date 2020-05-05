from django.urls import path, re_path
from . import views

app_name = "expenses"
urlpatterns = [
    path(
        route='',
        view=views.MonthlyExpensesListView.as_view(),
        name='list'
    ),
    re_path(
        route=r'^(?P<date>\d{4}-\d{2})/$', view=views.MonthView.as_view(), name='month'
    )
]

from django.urls import path, include
from .views import TabularReportView, ImportDataSourceView

urlpatterns = [
    path('sales-trends/', TabularReportView.as_view(), name='sales-trends'),
    path('importdata/', ImportDataSourceView.as_view(), name='import-data'),
]


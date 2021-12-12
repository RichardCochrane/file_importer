from django.contrib import admin
from django.urls import path

from api import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('heartbeat/', views.heartbeat_view, name='heartbeat'),
    path('api/v1/transactions/import', views.import_transactions_view, name='import_transactions'),
    path('api/v1/transactions/query', views.query_transactions_view, name='query_transactions'),
]

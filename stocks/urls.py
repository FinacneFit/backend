from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('search/', views.stock_search, name='stock_search'),
]
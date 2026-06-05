from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('questions/', views.question_list, name='question_list'),
    path('responses/', views.submit_response, name='submit_response'),
    path('profiles/me/', views.my_profile, name='my_profile'),
]
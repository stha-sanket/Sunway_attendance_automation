# notifier/urls.py
from django.urls import path
from . import views

app_name = 'notifier' # Namespace for URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('send-emails/', views.trigger_email_process, name='send_emails'),
]
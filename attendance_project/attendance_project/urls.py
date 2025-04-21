# attendance_project/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notifier.urls')), # Include notifier app's URLs at the root
]
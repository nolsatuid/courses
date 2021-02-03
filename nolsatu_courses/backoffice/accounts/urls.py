from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('sync-users/', views.sync_users, name='sync_users'),
]

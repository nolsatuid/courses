from django.urls import path

from . import views

app_name = 'nolsatu_app'
urlpatterns = [
    path('privacy_policy', views.privacy_policy, name='privacy_policy')
]

from django.urls import path
from . import views

app_name = "vendors"
urlpatterns = [
    path('list', views.VendorListView.as_view(), name='list'),
]

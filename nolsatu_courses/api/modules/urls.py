from django.urls import path
from . import views

app_name = "modules"
urlpatterns = [
    path('detail/<slug:slug>', views.ModuleDetailView.as_view(), name='detail')
]

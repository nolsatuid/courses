from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path('', views.OrderListView.as_view(), name='orders'),
    path('detail/<int:id>', views.DetailOrderView.as_view(), name='detail_orders'),
]

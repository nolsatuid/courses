from django.urls import path
from . import views

app_name = "carts"
urlpatterns = [
    path('add-item', views.AddToCartView.as_view(), name='add_item'),
    path('delete-item', views.DeleteItemCartView.as_view(), name='delete_item'),
    path('get-items', views.CartListView.as_view(), name='get_items'),
    path('checkout', views.CheckoutView.as_view(), name='checkout'),
    path('count-item', views.CartCountView.as_view(), name='count_item'),
]

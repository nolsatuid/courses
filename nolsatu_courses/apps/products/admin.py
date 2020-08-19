from django.contrib import admin
from .models import Product, Order, OrderItem, Cart


@admin.register(Product, site=admin.site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('course', 'price', 'code', 'discount_type', 'discount',)
    search_fields = ('course__title', 'code',)


@admin.register(Cart, site=admin.site)
class CartAdmin(admin.ModelAdmin):
    list_display = ('product', 'user',)
    search_fields = ('product__course__title', 'user__username',)


@admin.register(Order, site=admin.site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'user', 'status', 'grand_total', 'remote_transaction_id',)
    search_fields = ('number', 'user__username',)


@admin.register(OrderItem, site=admin.site)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'name',)
    search_fields = ('order__number', 'name',)

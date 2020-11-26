from django.contrib import admin

from .models import *


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_products', 'qty', 'start_date', 'end_date')


@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'user', 'status')

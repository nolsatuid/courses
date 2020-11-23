from django.contrib import admin

from .models import *


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code',)


@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher',)

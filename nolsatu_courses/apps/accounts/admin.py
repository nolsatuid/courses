from django.contrib import admin
from .models import MemberNolsatu


@admin.register(MemberNolsatu)
class AdminMemberNolsatu(admin.ModelAdmin):
    list_display = ('user', 'id_nolsatu', 'phone_number')
    search_fields = ('user__username', 'phone_number')

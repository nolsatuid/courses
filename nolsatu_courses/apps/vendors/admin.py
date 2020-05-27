from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VenderCourses(admin.ModelAdmin):
    filter_horizontal = ('users',)
    list_display = ('name',)
    search_fields = ('name',)

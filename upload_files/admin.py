from django.contrib import admin
from .models import UploadFile

@admin.register(UploadFile)
class AdminUploadFile(admin.ModelAdmin):
    list_display = ('name', 'file', 'description')
    search_fields = ('name',)

from django.contrib import admin
from .models import (
    Courses, Module, Section, TaskUploadSettings, Batch,
    Enrollment
)


@admin.register(Courses)
class AdminCourses(admin.ModelAdmin):
    list_display = ('title', 'level', 'category_list', 'is_visible', 'author')
    search_fields = ('title',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('category')

    def category_list(self, obj):
        return ", ".join(o.name for o in obj.category.all())


@admin.register(Module)
class AdminModule(admin.ModelAdmin):
    list_display = ('title', 'order', 'course', 'is_visible')
    search_fields = ('title',)


@admin.register(Section)
class AdminSection(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'is_task', 'is_visible')
    search_fields = ('title',)


@admin.register(TaskUploadSettings)
class AdminTaskUploadSettings(admin.ModelAdmin):
    list_display = ('section', 'allowed_extension_list', 'max_size',)
    search_fields = ('section',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('allowed_extension')

    def allowed_extension_list(self, obj):
        return ", ".join(o.name for o in obj.allowed_extension.all())


@admin.register(Batch)
class AdminBatch(admin.ModelAdmin):
    list_display = ('batch', 'start_date', 'end_date', 'is_active')
    search_fields = ('batch',)


@admin.register(Enrollment)
class AdminEnrollment(admin.ModelAdmin):
    list_display = (
        'batch', 'user', 'course', 'allowed_access', 'status',
        'date_enrollment', 'finishing_date'
    )
    search_fields = ('batch', 'user', 'course')

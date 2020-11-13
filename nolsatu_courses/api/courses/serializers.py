from django.conf import settings
from rest_framework import serializers

from nolsatu_courses.api.courses.utils import prepare_markdown
from nolsatu_courses.apps.courses.models import ( Courses, Batch, Enrollment,
                                                  Section, Module, TaskUploadSettings)
from nolsatu_courses.apps.products.models import Product
from nolsatu_courses.apps.vendors.models import Vendor


class BatchDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ('batch', 'start_date', 'end_date')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')
    level = serializers.CharField(source='get_level_display')
    status = serializers.CharField(source='get_status_display')
    categories = serializers.CharField(source='category_list')
    short_description = serializers.SerializerMethodField()
    product = ProductSerializer(required=False)
    vendor = VendorSerializer(required=False)

    def get_short_description(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.short_description_md)
        else:
            return obj.short_description

    class Meta:
        model = Courses
        fields = ['id', 'title', 'author', 'featured_image', 'level', 'status', 'categories', 
                  'short_description', 'is_allowed', 'quizzes', 'product', 'slug', 'level', 'vendor']


class CourseDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')
    level = serializers.CharField(source='get_level_display')
    categories = serializers.CharField(source='category_list')
    description = serializers.SerializerMethodField()

    def get_description(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.description_md)
        else:
            return obj.description

    class Meta:
        model = Courses
        fields = ['id', 'title', 'author', 'featured_image', 'level', 'categories', 'description', 'is_allowed',
                  'status', 'quizzes']


class EnrollDetailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Enrollment
        exclude = ("batch", "course", "user", "id")


class CourseDetailMergeSerializer(serializers.Serializer):
    course = CourseDetailSerializer()
    batch = BatchDetailSerializer(required=False)


class CourseEnrollSerializer(serializers.Serializer):
    can_register = serializers.BooleanField()
    has_enrolled = serializers.BooleanField()
    enroll = EnrollDetailSerializer()


class SectionPreviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'title', 'is_visible']


class ModulePreviewListSerializer(serializers.ModelSerializer):
    sections = SectionPreviewListSerializer(many=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'is_visible', 'sections']


class CoursePreviewListSerializer(serializers.ModelSerializer):
    modules = ModulePreviewListSerializer(many=True)

    class Meta:
        model = Courses
        fields = ['modules']


class ModulePreviewSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    def get_description(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.description_md)
        else:
            return obj.description

    class Meta:
        model = Module
        fields = ['title', 'description']


class SectionPreviewSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    def get_content(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.content_md)
        else:
            return obj.content

    class Meta:
        model = Section
        fields = ['title', 'content']


class ModuleSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    def get_description(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.description_md)
        else:
            return obj.description

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'slug', 'order', 'is_visible', 'course']


class TaskSettingSerializer(serializers.ModelSerializer):
    instruction = serializers.SerializerMethodField()

    def get_instruction(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.instruction_md)
        else:
            return obj.instruction

    class Meta:
        model = TaskUploadSettings
        fields = ['id', 'instruction', 'max_size', 'section']


class SectionSerializer(serializers.ModelSerializer):
    task_setting = TaskSettingSerializer(required=False)
    content = serializers.SerializerMethodField()

    def get_content(self, obj) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.content_md)
        else:
            return obj.content

    class Meta:
        model = Section
        fields = ['id', 'title', 'slug', 'content', 'order', 'is_visible', 'is_task', 'module', 'files', 'task_setting']


class PaginationSerializer(serializers.Serializer):
    next_id = serializers.IntegerField()
    next_type = serializers.CharField()
    prev_id = serializers.IntegerField()
    prev_type = serializers.CharField()


class ModuleDetailSerializer(serializers.Serializer):
    is_complete_tasks = serializers.BooleanField()
    module = ModuleSerializer()
    pagination = PaginationSerializer()


class SectionDetailSerializer(serializers.Serializer):
    is_complete_tasks = serializers.BooleanField()
    section = SectionSerializer()
    pagination = PaginationSerializer()


class CollectTaskSerializer(serializers.Serializer):
    message = serializers.CharField()
    status = serializers.IntegerField()


class SectionTrackingListSerializer(serializers.ModelSerializer):
    on_activity = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'title', 'on_activity']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def get_on_activity(self, obj) -> bool:
        return obj.on_activity(self.user)


class ModuleTrackingListSerializer(serializers.ModelSerializer):
    on_activity = serializers.SerializerMethodField()
    sections = None

    class Meta:
        model = Module
        fields = ['id', 'title', 'on_activity', 'sections']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        self.fields['sections'] = SectionTrackingListSerializer(many=True, user=self.user)
        super().__init__(*args, **kwargs)

    def get_on_activity(self, obj) -> bool:
        return obj.on_activity(self.user)


class CourseTrackingListSerializer(serializers.ModelSerializer):
    modules = None

    class Meta:
        model = Courses
        fields = ['modules']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.fields['modules'] = ModuleTrackingListSerializer(many=True, user=self.user)
        super().__init__(*args, **kwargs)


class UserReportTaskSerializer(serializers.Serializer):
    section_name = serializers.CharField()
    score = serializers.FloatField(max_value=100, min_value=0)
    note = serializers.CharField(allow_blank=True)
    create_at = serializers.DateTimeField()
    update_at = serializers.DateTimeField()


class MyQuizSerializer(serializers.Serializer):
    name = serializers.CharField()
    score = serializers.FloatField(max_value=100, min_value=0)


class MyCourseSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')
    level = serializers.CharField(source='get_level_display')
    categories = serializers.CharField(source='category_list')
    short_description = serializers.SerializerMethodField()
    enroll_status = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    def get_progress(self, obj: Courses) -> float:
        return obj.progress_percentage(self.context['request'].user)

    def get_enroll_status(self, obj: Courses) -> str:
        return obj.get_enroll(self.context['request'].user).get_status_display()

    def get_short_description(self, obj: Courses) -> str:
        if settings.FEATURE.get("MARKDOWN_CONTENT"):
            return prepare_markdown(obj.short_description_md)
        else:
            return obj.short_description

    class Meta:
        model = Courses
        fields = ['id', 'title', 'author', 'featured_image', 'level', 'categories',
                  'short_description', 'slug', 'enroll_status', 'progress']


from rest_framework import serializers

from nolsatu_courses.apps.courses.models import Courses, Batch, Enrollment, Section, Module


class BatchDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Batch
        fields = ('batch', 'start_date', 'end_date')


class CourseSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')
    level = serializers.CharField(source='get_level_display')

    class Meta:
        model = Courses
        exclude = ['users', 'slug', 'description', 'is_visible']


class CourseDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')
    level = serializers.CharField(source='get_level_display')

    class Meta:
        model = Courses
        exclude = ['users', 'short_description', 'is_visible']


class EnrollDetailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Enrollment
        exclude = ("batch", "course", "user", "id")


class CourseDetailMergeSerializer(serializers.Serializer):
    course = CourseDetailSerializer()
    batch = BatchDetailSerializer()


class CourseEnrollSerializer(serializers.Serializer):
    has_enrolled = serializers.BooleanField()
    enroll = EnrollDetailSerializer()


class SectionPreviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'title', 'slug', 'is_visible']


class ModulePreviewListSerializer(serializers.ModelSerializer):
    sections = SectionPreviewListSerializer(many=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'slug', 'is_visible', 'sections']


class CoursePreviewListSerializer(serializers.ModelSerializer):
    modules = ModulePreviewListSerializer(many=True)

    class Meta:
        model = Courses
        fields = ['modules']


class ModulePreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = ['title', 'description']


class SectionPreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ['title', 'content']


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = '__all__'


class PaginationSerializer(serializers.Serializer):
    next_page = serializers.CharField()
    prev_page = serializers.CharField()


class ModuleDetailSerializer(serializers.Serializer):
    module = ModuleSerializer()
    pagination = PaginationSerializer()


class SectionDetailSerializer(serializers.Serializer):
    section = SectionSerializer()
    pagination = PaginationSerializer()


class SectionTrackingListSerializer(serializers.ModelSerializer):
    url_detail = serializers.CharField(source='api_detail_url')
    on_activity = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['id', 'title', 'on_activity', 'url_detail']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def get_on_activity(self, obj):
        return obj.on_activity(self.user)


class ModuleTrackingListSerializer(serializers.ModelSerializer):
    url_detail = serializers.CharField(source='api_detail_url')
    on_activity = serializers.SerializerMethodField()
    sections = None

    class Meta:
        model = Module
        fields = ['id', 'title', 'on_activity', 'url_detail', 'sections']

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        self.fields['sections'] = SectionTrackingListSerializer(many=True, user=self.user)
        super().__init__(*args, **kwargs)

    def get_on_activity(self, obj):
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

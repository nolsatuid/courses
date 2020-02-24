from rest_framework import serializers

from nolsatu_courses.apps.courses.models import Courses, Batch, Enrollment


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

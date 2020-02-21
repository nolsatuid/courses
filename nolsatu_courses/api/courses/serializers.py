from rest_framework import serializers

from nolsatu_courses.apps.courses.models import Courses


class CourseSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')

    class Meta:
        model = Courses
        exclude = ['users', 'slug', 'description', 'is_visible']


class CourseDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    featured_image = serializers.CharField(source='featured_image_with_host')

    class Meta:
        model = Courses
        exclude = ['users', 'slug', 'short_description', 'is_visible']

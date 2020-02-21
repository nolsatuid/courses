from rest_framework import serializers

from nolsatu_courses.apps.courses.models import Courses


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        exclude = ['users', 'slug', 'description', 'is_visible']


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        exclude = ['users', 'slug', 'short_description', 'is_visible']

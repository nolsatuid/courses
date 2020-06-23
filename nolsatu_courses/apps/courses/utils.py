import json

from io import StringIO
from rest_framework import serializers
from nolsatu_courses.apps.courses.models import (
    Courses, Module, Section, TaskUploadSettings
)


class ExportCourse:

    def __init__(self, course):
        self.serializer = ExportCourseSerializer(course)
        self.data = self.serializer.data

    def json_buffer(self):
        buffer = StringIO(json.dumps(self.data, indent=4))
        return buffer


class TaskSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskUploadSettings
        exclude = ['section']


class ExportSectionSerializer(serializers.ModelSerializer):
    task_setting = TaskSettingSerializer(required=False)

    class Meta:
        model = Section
        exclude = ['module', 'files']


class ExportModuleSerializer(serializers.ModelSerializer):
    sections = ExportSectionSerializer(many=True)

    class Meta:
        model = Module
        exclude = ['course']


class ExportCourseSerializer(serializers.ModelSerializer):
    modules = ExportModuleSerializer(many=True)

    class Meta:
        model = Courses
        exclude = ['author', 'users', 'quizzes', 'vendor']

from rest_framework import serializers

from nolsatu_courses.apps.courses.models import Module


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = '__all__'


class PaginationSerializer(serializers.Serializer):
    next_slug = serializers.CharField()
    next_type = serializers.CharField()
    prev_slug = serializers.CharField()
    prev_type = serializers.CharField()


class ModuleDetailSerializer(serializers.Serializer):
    module = ModuleSerializer()
    pagination = PaginationSerializer()

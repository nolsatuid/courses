from rest_framework import serializers


class MessageSuccesSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorMessageSerializer(serializers.Serializer):
    detail = serializers.CharField()
    error_message = serializers.CharField()
    message = serializers.CharField()
    error_code = serializers.CharField()

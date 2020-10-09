from rest_framework import serializers

from nolsatu_courses.apps.products.models import Order


# Here add your serializer


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    number = serializers.CharField(max_length=50)
    status = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Order
        fields = ['id', 'number', 'status', 'created_at']
        read_only_fields = ['id', 'number', 'status', 'created_at']

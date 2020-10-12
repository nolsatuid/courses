from rest_framework import serializers

from nolsatu_courses.apps.products.models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_status(self, obj) -> str:
        return obj.get_status_display()

    class Meta:
        model = Order
        fields = ['id', 'number', 'status', 'created_at']
        read_only_fields = ['id', 'number', 'status', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    def get_status(self, obj) -> str:
        return obj.get_status_display()

    class Meta:
        model = Order
        exclude = ('user', )
        read_only_fields = ('id', 'user', 'number', 'remote_transaction_id', 'grand_total')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'price', 'name']
        read_only_fields = ['id', 'price', 'name']

from rest_framework import serializers

from nolsatu_courses.api.courses.serializers import ProductSerializer


# Here add your serializer

class AddCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartIDSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.UUIDField()
    )


class CartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product = ProductSerializer()

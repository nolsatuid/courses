from rest_framework import serializers


# Here add your serializer

class AddCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartIDSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.UUIDField()
    )

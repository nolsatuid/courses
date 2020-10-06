from rest_framework import serializers

from nolsatu_courses.apps.products.models import Cart, Product


# Here add your serializer

class AddCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartIDSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.UUIDField()
    )


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course = serializers.CharField()
    price = serializers.IntegerField()
    code = serializers.CharField()
    discount_type = serializers.IntegerField()
    discount_value = serializers.IntegerField()
    discount = serializers.IntegerField()


class CartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product = ProductSerializer()

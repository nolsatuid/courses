from rest_framework import serializers

from nolsatu_courses.apps.products.models import Product


# Here add your serializer

class AddCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartIDSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.UUIDField()
    )


class ProductSerializer(serializers.ModelSerializer):
    course = serializers.IntegerField()

    class Meta:
        model = Product
        fields = "__all__"


class CartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product = ProductSerializer()

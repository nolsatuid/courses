from rest_framework import serializers

from nolsatu_courses.api.courses.serializers import ProductSerializer
from nolsatu_courses.apps.products.models import Product, Order, Cart


class AddCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class CartIDSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.UUIDField()
    )


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()

    class Meta:
        ref_name = 'CourseSerializer'


class ProductCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Product
        fields = "__all__"


class CartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product = ProductCourseSerializer()


class FullCartSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    carts = CartSerializer(many=True)


class CartCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()

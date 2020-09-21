from rest_framework import serializers

from nolsatu_courses.apps.vendors.models import Vendor


class VendorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ('id', 'users')

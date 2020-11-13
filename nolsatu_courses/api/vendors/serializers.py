from rest_framework import serializers

from nolsatu_courses.apps.vendors.models import Vendor


class VendorListSerializer(serializers.ModelSerializer):
    logo = serializers.CharField(source="get_logo_with_host")

    class Meta:
        model = Vendor
        exclude = ('id', 'users')

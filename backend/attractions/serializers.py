from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import NationalPark


class NationalParkGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = NationalPark
        geo_field = 'location'
        fields = ('id', 'name', 'code', 'state', 'description')

class NationalParkBoundarySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = NationalPark
        geo_field = 'polygon'
        fields = ('id', 'name', 'code', 'state', 'description')
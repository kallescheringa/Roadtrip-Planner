from rest_framework import generics
from .models import NationalPark
from .serializers import NationalParkGeoSerializer, NationalParkBoundarySerializer


class NationalParkListView(generics.ListAPIView):
    queryset = NationalPark.objects.all()
    serializer_class = NationalParkGeoSerializer


class NationalParkBoundaryListView(generics.ListAPIView):
    queryset = NationalPark.objects.exclude(polygon__isnull=True)
    serializer_class = NationalParkBoundarySerializer
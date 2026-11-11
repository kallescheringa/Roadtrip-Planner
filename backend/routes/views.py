import json

from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attractions.models import NationalPark
from routing_engine.geocoding import geocode
from routing_engine.osrm_client import get_route
from .models import Route, RouteStop


class PlanRouteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        start_name = request.data.get('start')
        end_name = request.data.get('end')
        stop_names = request.data.get('stops', [])
        cyclic = request.data.get('cyclic', False)
        route_name = request.data.get('name', '')

        if not start_name or not end_name:
            return Response(
                {'detail': 'Start and end locations are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Geocode everything
        start_coords = geocode(start_name)
        if not start_coords:
            return Response({'detail': f'Could not find location: {start_name}'}, status=400)

        end_coords = geocode(end_name)
        if not end_coords:
            return Response({'detail': f'Could not find location: {end_name}'}, status=400)

        stop_coords = []
        for stop_name in stop_names:
            if not stop_name:
                continue
            coords = geocode(stop_name)
            if not coords:
                return Response({'detail': f'Could not find location: {stop_name}'}, status=400)
            stop_coords.append(coords)

        # Build waypoint list for OSRM
        waypoints = [start_coords] + stop_coords + [end_coords]
        if cyclic:
            waypoints.append(start_coords)  # return to start

        # Call OSRM
        try:
            osrm_result = get_route(waypoints)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)

        # Save the route
        path_geom = GEOSGeometry(json.dumps(osrm_result['geometry']))

        route = Route.objects.create(
            user=request.user,
            name=route_name,
            start=Point(*start_coords),
            end=Point(*end_coords),
            cyclic=cyclic,
            path=path_geom,
        )

        for i, coords in enumerate(stop_coords):
            RouteStop.objects.create(route=route, location=Point(*coords), order=i)

        # Find nearby parks (within 25 miles of the route path)
        nearby_parks = NationalPark.objects.filter(
            location__dwithin=(path_geom, D(mi=25))
        ).annotate(
            distance=Distance('location', path_geom)
        ).order_by('distance')

        parks_data = [
            {
                'id': p.id,
                'name': p.name,
                'code': p.code,
                'state': p.state,
                'distance_miles': round(p.distance.mi, 1),
                'lat': p.location.y,
                'lon': p.location.x,
            }
            for p in nearby_parks
        ]

        return Response({
            'route_id': route.id,
            'path': osrm_result['geometry'],  # GeoJSON LineString for frontend
            'distance_miles': round(osrm_result['distance'] / 1609.34, 1),
            'duration_hours': round(osrm_result['duration'] / 3600, 1),
            'nearby_parks': parks_data,
        }, status=status.HTTP_201_CREATED)
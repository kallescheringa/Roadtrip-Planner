import json

from decouple import config
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand
import requests

from attractions.models import NationalPark

BOUNDARY_URL_TEMPLATE = "https://developer.nps.gov/api/v1/mapdata/parkboundaries/{code}"


class Command(BaseCommand):
    help = "Fetch official NPS boundary polygons and attach them to existing NationalPark rows"

    def handle(self, *args, **options):
        api_key = config('NPS_API_KEY')
        parks = NationalPark.objects.all()
        matched, skipped = 0, 0

        for park in parks:
            url = BOUNDARY_URL_TEMPLATE.format(code=park.code)
            resp = requests.get(url, params={'api_key': api_key})

            if resp.status_code != 200:
                self.stdout.write(self.style.WARNING(f"Skipping {park.code} — HTTP {resp.status_code}"))
                skipped += 1
                continue

            data = resp.json()
            features = data.get('features', [])
            if not features:
                self.stdout.write(self.style.WARNING(f"Skipping {park.code} — no boundary features"))
                skipped += 1
                continue

            geom = features[0].get('geometry')
            if not geom:
                self.stdout.write(self.style.WARNING(f"Skipping {park.code} — no geometry in feature"))
                skipped += 1
                continue

            geos_geom = GEOSGeometry(json.dumps(geom))

            if geos_geom.geom_type == 'Polygon':
                geos_geom = MultiPolygon(geos_geom)

            park.polygon = geos_geom
            park.save()
            matched += 1
            self.stdout.write(f"Matched {park.code}")

        self.stdout.write(self.style.SUCCESS(f"Done. Matched: {matched}, Skipped: {skipped}"))
import json

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand
import requests

NRCAN_URL = (
    "https://proxyinternet.nrcan-rncan.gc.ca/arcgis/rest/services/"
    "CLSS-SATC/CLSS_Administrative_Boundaries/MapServer/1/query"
)


class Command(BaseCommand):
    help = "Fetch Canadian national park boundaries from NRCAN and attach to Canadian NationalPark rows"

    def handle(self, *args, **options):
        params = {
            'where': "distributionType IN ('NP', 'NPR')",
            'outFields': 'adminAreaNameEng,NID,distributionType',
            'f': 'geojson',
        }
        resp = requests.get(NRCAN_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        from attractions.models import NationalPark

        matched, skipped = 0, 0

        for feature in data['features']:
            name = feature['properties'].get('adminAreaNameEng', '').strip()
            geom = feature.get('geometry')
            if not name or not geom:
                skipped += 1
                continue

            try:
                # Normalize NRCAN's "BANFF NATIONAL PARK OF CANADA" to just "banff"
                normalized_name = name.upper().split(' NATIONAL PARK')[0].strip()
                # Match against our seeded parks (which are title case, e.g. "Banff National Park")
                park = NationalPark.objects.get(name__icontains=normalized_name, country='CA')
            except NationalPark.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Skipping {name} — no matching park in DB"))
                skipped += 1
                continue

            geos_geom = GEOSGeometry(json.dumps(geom))

            if geos_geom.geom_type == 'Polygon':
                geos_geom = MultiPolygon(geos_geom)

            park.polygon = geos_geom
            park.save()
            matched += 1
            self.stdout.write(f"Matched {name}")

        self.stdout.write(self.style.SUCCESS(f"Done. Matched: {matched}, Skipped: {skipped}"))
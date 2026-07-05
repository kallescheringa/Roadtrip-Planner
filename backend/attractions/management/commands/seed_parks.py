from decouple import config
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
import requests

from attractions.models import NationalPark

NPS_API_URL = "https://developer.nps.gov/api/v1/parks"


class Command(BaseCommand):
    help = "Fetch national parks from the NPS API and seed the database"

    def handle(self, *args, **options):
        api_key = config('NPS_API_KEY')
        params = {'api_key': api_key, 'limit': 600}
        created, updated = 0, 0

        while True:
            resp = requests.get(NPS_API_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            for entry in data['data']:
                if 'National Park' not in entry['designation']:
                    continue  # skip monuments, seashores, etc — only true national parks

                lat = entry.get('latitude')
                lon = entry.get('longitude')
                if not lat or not lon:
                    self.stdout.write(self.style.WARNING(f"Skipping {entry['name']} — no coordinates"))
                    continue

                states = entry.get('states', '').split(',')
                state = states[0] if states else ''

                park, was_created = NationalPark.objects.update_or_create(
                    code=entry['parkCode'],
                    defaults={
                        'name': entry['fullName'],
                        'description': entry.get('description', ''),
                        'location': Point(float(lon), float(lat)),
                        'country': 'US',
                        'state': state,
                    },
                )
                created += was_created
                updated += not was_created

            if int(params.get('start', 0)) + len(data['data']) >= int(data['total']):
                break
            params['start'] = int(params.get('start', 0)) + len(data['data'])

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}"))
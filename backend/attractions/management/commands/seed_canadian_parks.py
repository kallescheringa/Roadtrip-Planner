from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from attractions.models import NationalPark

# Curated list — Parks Canada's official National Parks (not Historic Sites or Marine Conservation Areas)
CANADIAN_PARKS = [
    {"code": "banf_ca", "name": "Banff National Park", "province": "AB", "lat": 51.4968, "lon": -115.9281},
    {"code": "jasp_ca", "name": "Jasper National Park", "province": "AB", "lat": 52.8734, "lon": -117.9543},
    {"code": "wate_ca", "name": "Waterton Lakes National Park", "province": "AB", "lat": 49.0833, "lon": -113.9},
    {"code": "elki_ca", "name": "Elk Island National Park", "province": "AB", "lat": 53.5964, "lon": -112.8546},
    {"code": "wood_ca", "name": "Wood Buffalo National Park", "province": "AB", "lat": 59.5, "lon": -112.5},
    {"code": "yoho_ca", "name": "Yoho National Park", "province": "BC", "lat": 51.4383, "lon": -116.4858},
    {"code": "koot_ca", "name": "Kootenay National Park", "province": "BC", "lat": 50.8, "lon": -116.05},
    {"code": "glac_ca", "name": "Glacier National Park", "province": "BC", "lat": 51.25, "lon": -117.5167},
    {"code": "reve_ca", "name": "Mount Revelstoke National Park", "province": "BC", "lat": 51.05, "lon": -118.15},
    {"code": "paci_ca", "name": "Pacific Rim National Park Reserve", "province": "BC", "lat": 49.0, "lon": -125.6},
    {"code": "gwai_ca", "name": "Gwaii Haanas National Park Reserve", "province": "BC", "lat": 52.2, "lon": -131.4},
    {"code": "gulf_ca", "name": "Gulf Islands National Park Reserve", "province": "BC", "lat": 48.78, "lon": -123.35},
    {"code": "rimo_ca", "name": "Riding Mountain National Park", "province": "MB", "lat": 50.6531, "lon": -100.0322},
    {"code": "wapu_ca", "name": "Wapusk National Park", "province": "MB", "lat": 58.6667, "lon": -93.4},
    {"code": "fund_ca", "name": "Fundy National Park", "province": "NB", "lat": 45.5989, "lon": -64.9486},
    {"code": "kouc_ca", "name": "Kouchibouguac National Park", "province": "NB", "lat": 46.8, "lon": -64.9667},
    {"code": "gros_ca", "name": "Gros Morne National Park", "province": "NL", "lat": 49.6, "lon": -57.75},
    {"code": "terr_ca", "name": "Terra Nova National Park", "province": "NL", "lat": 48.5333, "lon": -53.9667},
    {"code": "torn_ca", "name": "Torngat Mountains National Park", "province": "NL", "lat": 59.35, "lon": -63.7},
    {"code": "auyu_ca", "name": "Auyuittuq National Park", "province": "NU", "lat": 67.8973, "lon": -65.2145},
    {"code": "sirm_ca", "name": "Sirmilik National Park", "province": "NU", "lat": 72.75, "lon": -80.5},
    {"code": "qutt_ca", "name": "Quttinirpaaq National Park", "province": "NU", "lat": 82.0, "lon": -70.0},
    {"code": "ukku_ca", "name": "Ukkusiksalik National Park", "province": "NU", "lat": 64.9, "lon": -89.6},
    {"code": "cabr_ca", "name": "Cape Breton Highlands National Park", "province": "NS", "lat": 46.75, "lon": -60.6667},
    {"code": "keji_ca", "name": "Kejimkujik National Park", "province": "NS", "lat": 44.4, "lon": -65.2},
    {"code": "brup_ca", "name": "Bruce Peninsula National Park", "province": "ON", "lat": 45.2167, "lon": -81.5333},
    {"code": "geor_ca", "name": "Georgian Bay Islands National Park", "province": "ON", "lat": 44.85, "lon": -79.9},
    {"code": "pele_ca", "name": "Point Pelee National Park", "province": "ON", "lat": 41.9667, "lon": -82.5167},
    {"code": "thou_ca", "name": "Thousand Islands National Park", "province": "ON", "lat": 44.3333, "lon": -76.1667},
    {"code": "pukw_ca", "name": "Pukaskwa National Park", "province": "ON", "lat": 48.2, "lon": -85.9},
    {"code": "pei__ca", "name": "Prince Edward Island National Park", "province": "PE", "lat": 46.4667, "lon": -63.25},
    {"code": "forl_ca", "name": "Forillon National Park", "province": "QC", "lat": 48.85, "lon": -64.35},
    {"code": "lamu_ca", "name": "La Mauricie National Park", "province": "QC", "lat": 46.6833, "lon": -72.85},
    {"code": "ming_ca", "name": "Mingan Archipelago National Park Reserve", "province": "QC", "lat": 50.2667, "lon": -63.65},
    {"code": "gras_ca", "name": "Grasslands National Park", "province": "SK", "lat": 49.1167, "lon": -107.5},
    {"code": "prin_ca", "name": "Prince Albert National Park", "province": "SK", "lat": 53.9167, "lon": -106.4167},
    {"code": "naha_ca", "name": "Nahanni National Park Reserve", "province": "NT", "lat": 61.75, "lon": -125.5},
    {"code": "aulv_ca", "name": "Aulavik National Park", "province": "NT", "lat": 73.75, "lon": -119.5},
    {"code": "tukt_ca", "name": "Tuktut Nogait National Park", "province": "NT", "lat": 68.75, "lon": -122.0},
    {"code": "ivva_ca", "name": "Ivvavik National Park", "province": "YT", "lat": 69.3667, "lon": -139.4},
    {"code": "vunt_ca", "name": "Vuntut National Park", "province": "YT", "lat": 68.35, "lon": -139.9},
]


class Command(BaseCommand):
    help = "Seed Canadian national parks (static curated list — Parks Canada has no equivalent public REST API to NPS)"

    def handle(self, *args, **options):
        created, updated = 0, 0

        for entry in CANADIAN_PARKS:
            park, was_created = NationalPark.objects.update_or_create(
                code=entry['code'],
                defaults={
                    'name': entry['name'],
                    'description': '',
                    'location': Point(entry['lon'], entry['lat']),
                    'country': 'CA',
                    'state': entry['province'],
                },
            )
            created += was_created
            updated += not was_created

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}"))
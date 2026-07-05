from django.contrib.gis.db import models


class Attraction(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.PointField(geography=True)
    country = models.CharField(max_length=2)  # ISO 3166-1 alpha-2, e.g. "US"

    def __str__(self):
        return self.name


class NationalPark(Attraction):
    polygon = models.MultiPolygonField(geography=True)
    state = models.CharField(max_length=2)
    code = models.CharField(max_length=10, unique=True)  # NPS park code, e.g. "yell"

    def __str__(self):
        return f"{self.name} ({self.code})"
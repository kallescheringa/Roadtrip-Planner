from django.conf import settings
from django.contrib.gis.db import models


class Route(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='routes',
    )
    name = models.CharField(max_length=255, blank=True)
    start = models.PointField(geography=True)
    end = models.PointField(geography=True)
    cyclic = models.BooleanField(default=False)
    path = models.LineStringField(geography=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Route {self.pk}"


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    location = models.PointField(geography=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Stop {self.order} on {self.route}"
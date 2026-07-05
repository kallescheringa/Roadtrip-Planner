from django.contrib.gis import admin

from .models import Route, RouteStop


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1


@admin.register(Route)
class RouteAdmin(admin.GISModelAdmin):
    list_display = ('name', 'user', 'cyclic', 'created_at')
    inlines = [RouteStopInline]
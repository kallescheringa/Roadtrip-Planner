from django.contrib.gis import admin

from .models import Attraction, NationalPark


@admin.register(Attraction)
class AttractionAdmin(admin.GISModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)


@admin.register(NationalPark)
class NationalParkAdmin(admin.GISModelAdmin):
    list_display = ('name', 'code', 'state')
    search_fields = ('name', 'code')
from django.urls import path
from .views import NationalParkListView, NationalParkBoundaryListView

urlpatterns = [
    path('parks/', NationalParkListView.as_view(), name='park-list'),
    path('parks/boundaries/', NationalParkBoundaryListView.as_view(), name='park-boundaries'),
]
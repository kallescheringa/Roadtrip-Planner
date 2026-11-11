from django.urls import path
from .views import PlanRouteView

urlpatterns = [
    path('plan/', PlanRouteView.as_view(), name='plan-route'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupportIncidentViewSet

router = DefaultRouter()
router.register(r'incidents', SupportIncidentViewSet, basename='incident')

urlpatterns = [
    path('', include(router.urls)),
]

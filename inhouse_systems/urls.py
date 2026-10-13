from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InHouseSystemViewSet

router = DefaultRouter()
router.register(r'inhouse', InHouseSystemViewSet, basename='inhouse')

urlpatterns = [
    path('', include(router.urls)),
]

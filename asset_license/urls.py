from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HardwareAssetViewSet,
    SoftwareLicenseViewSet,
    AssetUserViewSet,
    AssetBrandViewSet,
    AssetModelViewSet,
)

router = DefaultRouter()
router.register(r'hardware', HardwareAssetViewSet, basename='hardware')
router.register(r'licenses', SoftwareLicenseViewSet, basename='license')
router.register(r'users', AssetUserViewSet, basename='asset-user')
router.register(r'brands', AssetBrandViewSet, basename='asset-brand')
router.register(r'models', AssetModelViewSet, basename='asset-model')

urlpatterns = [
    path('', include(router.urls)),
]

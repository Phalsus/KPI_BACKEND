from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KPIMasterViewSet, CustomWorkLogViewSet

router = DefaultRouter()
router.register(r'kpis', KPIMasterViewSet, basename='kpimaster')
router.register(r'work-logs', CustomWorkLogViewSet, basename='worklog')

urlpatterns = [
    path('', include(router.urls)),
]

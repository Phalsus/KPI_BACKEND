from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyCheckinViewSet

router = DefaultRouter()
router.register(r'checkins', DailyCheckinViewSet, basename='checkin')

urlpatterns = [
    path('', include(router.urls)),
]

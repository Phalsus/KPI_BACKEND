from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearningRecordViewSet, BehavioralReviewRecordViewSet

router = DefaultRouter()
router.register(r'learning', LearningRecordViewSet, basename='learning')
router.register(r'behavioral', BehavioralReviewRecordViewSet, basename='behavioral')

urlpatterns = [
    path('', include(router.urls)),
]

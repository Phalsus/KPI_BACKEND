from django.urls import path
from .views import ScorecardSummaryView

urlpatterns = [
    path('summary/', ScorecardSummaryView.as_view(), name='scorecard_summary'),
]

from django.urls import path
from .views import AggregatedFeedView

app_name = 'newsfeed'

urlpatterns = [
    path('', AggregatedFeedView.as_view(), name='user_feed'),
]

# backend/newsfeed/urls.py

from django.urls import path
from .views import UserFeedView

app_name = 'newsfeed'

urlpatterns = [
    path('', UserFeedView.as_view(), name='user_feed'),
]

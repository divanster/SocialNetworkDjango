# backend/newsfeed/urls.py
from django.urls import path
from .views import UserFeedView

urlpatterns = [
    path('feed/', UserFeedView.as_view(), name='user_feed'),
]

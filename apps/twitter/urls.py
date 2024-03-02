from django.urls import path

from apps.twitter.views import FeedDataListAPI

urlpatterns = [
    path('feed', FeedDataListAPI.as_view())
]

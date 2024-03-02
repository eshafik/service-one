from rest_framework import serializers

from apps.twitter.models import FeedPost


class FeedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedPost
        fields = '__all__'

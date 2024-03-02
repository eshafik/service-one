import json

import pika
import requests
from django.conf import settings
from django.core.cache import cache
import redis
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from app_libs.rabbitmq_utils import publish_message
from apps.twitter.models import FeedPost
from apps.twitter.serializer import FeedPostSerializer


class FeedDataListAPI(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedPostSerializer
    tracer = trace.get_tracer(__name__)

    def get_queryset(self):
        with self.tracer.start_as_current_span('db_query'):
            queryset = FeedPost.objects.all()
            return queryset

    def list(self, request, *args, **kwargs):
        _type = self.request.query_params.get('type')
        response = requests.get(url=f'{settings.SERVICE_TWO_BASE_URL}/api/v1/twitters/feed?type={_type}')

        with self.tracer.start_as_current_span("send_rabbitmq_message"):
            # Serialize the current context into a carrier
            propagator = TraceContextTextMapPropagator()
            carrier = {}
            propagator.inject(carrier)

            # RabbitMQ allows us to include headers with our message
            properties = pika.BasicProperties(headers=carrier)
        publish_message(queue_name='test', message=json.dumps({'data': response.json().get('data'),
                                                               'user_id': request.user.id}),
                        properties=properties)
        return Response(data=response.json(), status=response.status_code)

    # der list
    # def get(self, request):
    #     tracer = trace.get_tracer(__name__)
    #     feed_post = cache.get("feed_post")
    #     if not feed_post:
    #         with tracer.start_as_current_span('db_query'):
    #             queryset = FeedPost.objects.all()
    #             serializer = FeedPostSerializer(queryset, many=True)
    #             feed_post = serializer.data
    #             cache.set("feed_post", feed_post)
    #     return Response(data=feed_post)
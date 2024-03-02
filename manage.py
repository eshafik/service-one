#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from django.conf import settings
from opentelemetry import trace
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_NAMESPACE
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
    try:
        from django.core.management import execute_from_command_line
        DjangoInstrumentor().instrument()
        RequestsInstrumentor().instrument()
        RedisInstrumentor().instrument()
        Psycopg2Instrumentor().instrument()
        resource = Resource(
            attributes={
                SERVICE_NAME: 'service_one',
                SERVICE_NAMESPACE: "Service One",
            }
        )
        traceProvider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTEL_TRACE_ENDPOINT))
        traceProvider.add_span_processor(processor)
        trace.set_tracer_provider(traceProvider)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

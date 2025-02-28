from fastapi import FastAPI
import os
from opentelemetry import propagate, trace, metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.propagators.aws import AwsXRayPropagator
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter


tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


def setup_instrumentation(
    app: FastAPI,
):
    FastAPIInstrumentor().instrument_app(
        app,
        excluded_urls=','.join([
            '/health'
        ])
    )
    BotocoreInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    AioHttpClientInstrumentor().instrument()
    CeleryInstrumentor().instrument()
    RedisInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    AsyncPGInstrumentor().instrument()



def setup_opentelemetry(tracer, meter):
    propagate.set_global_textmap(AwsXRayPropagator())
    # Service name is required for most backends
    resource_attributes = { 'service.name': 'openbot-api' }
    if (os.environ.get("OTEL_RESOURCE_ATTRIBUTES")):
        resource_attributes = None
    resource = Resource.create(attributes=resource_attributes)

    # Setting up Traces
    processor = BatchSpanProcessor(OTLPSpanExporter())
    tracer_provider = TracerProvider(
        resource=resource, 
        active_span_processor=processor,
        id_generator=AwsXRayIdGenerator())

    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)

    # Setting up Metrics
    metric_reader = PeriodicExportingMetricReader(exporter=OTLPMetricExporter(), export_interval_millis=1000)
    metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])

    metrics.set_meter_provider(metric_provider)
    meter = metrics.get_meter(__name__)
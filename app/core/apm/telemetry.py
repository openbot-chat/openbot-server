from opentelemetry import trace, metrics



tracer = trace.get_tracer_provider().get_tracer(__name__)
meter = metrics.get_meter_provider().get_meter(__name__)

from opentelemetry import trace


trace_manager = trace.get_tracer(__name__)


def trace(function):
    def inner(*args, **kwargs):
        with trace_manager.start_as_current_span(function.__name__):
            return function(*args, **kwargs)

    return inner

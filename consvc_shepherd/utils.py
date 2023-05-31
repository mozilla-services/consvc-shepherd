"""Utility module for common functions used in consvc-shepherd."""

import contextlib

import markus
from django.conf import settings


class ShepherdMetrics:
    """Instantiate a metrics instance for a given module."""

    def __init__(self, thing=__name__) -> None:
        self.metrics = markus.get_metrics(thing)

    def incr_if_enabled(
        self, name: str, value: int = 1, tags: str | None = None
    ) -> None:
        """Increment supplied metric by 1 (default) and add tags if specified."""
        if settings.STATSD_ENABLED:
            self.metrics.incr(name, value, tags)

    def histogram_if_enabled(
        self, name: str, value: int, tags: str | None = None
    ) -> None:
        """Histogram metric instance and add tags if specified."""
        if settings.STATSD_ENABLED:
            self.metrics.histogram(name, value=value, tags=tags)

    def gauge_if_enabled(self, name: str, value: int, tags: str | None = None) -> None:
        """Gauge metric instance and add tags if specified."""
        if settings.STATSD_ENABLED:
            self.metrics.gauge(name, value=value, tags=tags)

    def time_if_enabled(self, name: str, tags: str | None = None):
        """Time metric of execution of a function."""

        def timing_decorator(func):
            def func_wrapper(*args, **kwargs):
                ctx_manager = (
                    self.metrics.timer(name)
                    if settings.STATSD_ENABLED
                    else contextlib.nullcontext()
                )
                with ctx_manager:
                    return func(*args, **kwargs)

            return func_wrapper

        return timing_decorator

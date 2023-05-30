"""Utility module for common functions used in consvc-shepherd."""

import markus
from django.conf import settings

metrics = markus.get_metrics("shepherd")


def incr_if_enabled(name: str, value: int = 1, tags: str | None = None) -> None:
    """Increment supplied metric by 1 and add tags if specified."""
    if settings.STATSD_ENABLED:
        metrics.incr(name, value, tags)


def histogram_if_enabled(name: str, value: int, tags: str | None = None) -> None:
    """Histogram metric instance and add tags if specified."""
    if settings.STATSD_ENABLED:
        metrics.histogram(name, value=value, tags=tags)


def gauge_if_enabled(name: str, value: int, tags: str | None = None) -> None:
    """Gauge metric instance and add tags if specified."""
    if settings.STATSD_ENABLED:
        metrics.gauge(name, value=value, tags=tags)

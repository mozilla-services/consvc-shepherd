"""Utility module for common functions used in consvc-shepherd."""

import markus
from django.conf import settings

metrics = markus.get_metrics("shepherd")


def incr_if_enabled(name: str, value: int = 1, tags: str | None = None) -> None:
    """Increment supplied metric by 1 and add tag if specified."""
    if settings.STATSD_ENABLED:
        metrics.incr(name, value, tags)

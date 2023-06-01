# Shepherd Metrics
This documentation describes the statsd-style metrics emitted by consvc_shepherd.

## Metrics

consvc_shepherd uses [markus][markus] (metrics client) to emit statsd-style metrics like
counters, gauges, and timers. We use the [datadog extensions][dogstatsd], which
include tags for metrics. In the production instance of Shepherd, metrics are emitted as
[UDP packets][udp], collected by a local [telegraf][telegraf] forwarder, and
stored in [influxdb][influxdb]. In development, metrics are disabled by
default, but there is a way described below to view metrics in development via `nc`.

## Telegraf

[Telegraf](https://github.com/influxdata/telegraf) is a plugin-driven server agent written by the folks over at [InfluxData](https://influxdata.com) for collecting & reporting metrics. To understand the 
configuration for Mozilla services, please view the documentation in [cloudops-infra](https://github.com/mozilla-services/cloudops-infra/tree/master/libs/influx/k8s/charts/telegraf).

[markus]: https://markus.readthedocs.io/en/latest/index.html "Markus documentation"
[dogstatsd]: https://docs.datadoghq.com/developers/dogstatsd "dogstatsd documentation"
[udp]: https://en.wikipedia.org/wiki/User_Datagram_Protocol
[telegraf]: https://docs.influxdata.com/telegraf
[influxdb]: https://docs.influxdata.com/influxdb/latest/reference/key-concepts/

## Configuration

Configuration is controlled by these environment variables:

- `DJANGO_STATSD_ENABLED` (default `False`) - Enables / disables emitting metrics to a
  statsd server
- `STATSD_DEBUG` (default `False`) - Enables / disables metrics logging
- `STATSD_ENABLED` (default `False`) - Enables metrics, `True` if either
  `DJANGO_STATSD_ENABLED` or `STATSD_DEBUG` are `True`
- `STATSD_HOST` (default `"127.0.0.1"`) - statsd server IP
- `STATSD_PORT` (default `8125`) - statsd server port
- `STATSD_PREFIX` (default `"shepherd"`) - prefix for all metrics.
  Dashes (and maybe other values) are converted to periods.

With the defaults `DJANGO_STATSD_ENABLED=False` and `STATSD_DEBUG=False`, no metrics
are emitted. In deployments, `DJANGO_STATSD_ENABLED=True` and `STATSD_DEBUG=False`,
so metrics are emitted but do not appear in logs.

Deployment variables are set in `cloudops-infra` in the `configmap.yaml` file in the Shepherd directory.

## Development

By default, metrics are disabled in development. They must be enabled via an
environment variable or in the `.env` file.

Metrics are set, incremented and controlled by utility methods that are defined in the `ShepherdMetrics` class contained in the [consvc_shepherd/utils.py](../consvc_shepherd/utils.py) module:

- `time_if_enabled(name)`
- `incr_if_enabled(name, value=1, tags=None)`
- `histogram_if_enabled(name, value, tags=None)`
- `gauge_if_enabled(name, value, tags=None)`

Simply instantiate a `ShepherdMetrics` class in your module, passing to it the `thing` parameter as defined in the `markus` docs, which defines the prefix keys that will be generated. Be default, `thing` will be set to `__name__`. Instantiating this class calls `markus.get_metrics()` and returns `markus.main.MetricsInterface` under the hood, on which all these methods are called. Ths metrics class decouples the logic from direct calls to `markus.main.MetricsInterface` instances.  

```python
from consvc_shepherd.utils import ShepherdMetrics

metrics = ShepherdMetrics("shepherd")

metrics.incr_if_enabled("publication.success")
```
With `DJANGO_STATSD_ENABLED=True`, metrics are sent to the server identified by
`STATSD_HOST` and `STATSD_PORT`, using the [DatadogMetrics
backend][markus-datadogmetrics]. These are sent as UDP packets, which means
they are silently dropped if there is no server to receive them. In local
development on macOS, you can emulate a `statsd` server and see the metrics with:

```sh
nc -lu localhost 8125
```

With `STATSD_DEBUG=True`, metrics are sent to the `markus` log using the
[LoggingMetrics backend][markus-loggingmetrics]. They are displayed along
with other logs like `request.summary` from that service.

## Testing
When writing tests for metrics, they can be enabled via
[override_settings][override_settings], and captured for test assertions with
[MetricsMock][metricsmock]. For example:

```python
from django.test import TestCase, override_settings

from markus.testing import MetricsMock

from shepherd.utils import incr_if_enabled


def code_that_emits_metric() -> int:
    incr_if_enabled("code_called")
    return 1


class CodeTest(TestCase):
    @override_settings(STATSD_ENABLED=True)
    def test_code(self) -> None:
        with MetricsMock() as mm:
            assert code_that_emits_metric() == 1

        mm.assert_incr_once("shepherd.code_called")
```

When testing, note that the `STATSD_PREFIX` (default `"shepherd"`) is
in the emitted metric name, so in this example, the test is looking for
`"shepherd.code_called"`, not `"code_called"`.

`MetricsMock` has other useful helper methods, such as
[print_records()][print_records] to see all captured metrics. This can help
when determining what metrics code is emitting.

[markus-datadogmetrics]: https://markus.readthedocs.io/en/latest/backends.html#datadog-metrics
[markus-loggingmetrics]: https://markus.readthedocs.io/en/latest/backends.html#logging-metrics
[override_settings]: https://docs.djangoproject.com/en/4.2/topics/testing/tools/#django.test.override_settings
[metricsmock]: https://markus.readthedocs.io/en/latest/testing.html
[print_records]: https://markus.readthedocs.io/en/latest/testing.html#markus.testing.MetricsMock.print_records

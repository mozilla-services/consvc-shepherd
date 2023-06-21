# StatsD Client Library for Shepherd

* Status: Accepted
* Deciders: [@taddes], [@tiftran], [@ncloudioj]
* Date: 2023-05-30

[@taddes]: https://github.com/taddes
[@tiftran]: https://github.com/tiftran
[@ncloudioj]: https://github.com/ncloudioj


## Context and Problem Statement

Shepherd is currently a minimal Django Admin application used to create and publish snapshots of advertiser settings of Sponsored Tiles. The recent expansion of the service through the Project Honeycomb: Share-of-Voice epic [DISCO-2290] along with moving to a developer-driven Continuous Deployment model [DISCO-2208] necessitated discussion around application metrics and observability. Up to this point, we did not have any information to analyze Shepherd's internal state pre or post deploy aside from automated testing and manual testing.

## Decision Drivers

1. Easy to implement, provides necessary features. 
2. Does not require excessive customization to Shepherd that hinders current/future development.
3. Works well with synchronous Python web frameworks (Shepherd is using Django).
4. Has precedent of effective usage (is used at Mozilla by other teams with more mature Django applications).
5. Good documentation, engagement, and maintenance with broader community.
6. Easy testing (plus if testing/mocking framework provided). 
7. Fits into Rapid Release Model strategy — specifically, using the same libraries and frameworks across similarly shaped services owned by the same team.

## Considered Options

* A. Markus [pypi](https://pypi.org/project/markus/)
* B. Prometheus [pypi](https://pypi.org/project/prometheus-client/)
* C. statsd (pystatsd) [pypi](https://pypi.org/project/statsd/)
* D. aiodogstatsd [pypi](https://pypi.org/project/aiodogstatsd/)

## Decision Outcome

Chosen option:

* A. Markus

Markus essentially meets all our required needs with a number of significant features that provide great benefit. 
Most StatsD libraries are not excessively complicated, in that the core functions of calling an increment, gauge, timer and histogram.  Markus matches this need with added flexibility, in that you can define tags and filters when calling a given metric and define backends.

Even though aiodogstatsd is used in Merino and we'd like to aim to use the same library across services, it is not the appropriate choice for Shepherd. We do not require asynchronous features. Also, aiodogstatsd is harder to test and has significantly fewer features than Markus. This could hamper maintenance and development. Essentially, it would require more effort to do the same task with likely poorer outcomes.

Example:

To return a MetricsInterface instance (with a specified prefix):
```python
get_metrics("shepherd")
markus.get_metrics(thing='', extra='', filters=None)
```

`thing` is a prefix to use for keys 
`extra` adds bits to end of prefix
`filters`, list of filters to apply

**[Backends](https://markus.readthedocs.io/en/latest/backends.html)** - A significant feature Markus has over other libraries is the ability to define metrics backends. It comes with the `LoggingMetrics`, `LoggingRollupMetrics`, `StatsdMetrics`, `DatadogMetrics`, `CloudwatchMetrics` by default, handling numerous configuration optimizations. You can also define your own backend.

Example:

Define `markus.configure()` and append backends, passing backends parameter as list of dicts. Each dict defines a backend. Can do datadog and logger configs, for example.  Each backend has a class argument, options dict for configuration, filters list to apply to emitted metrics:

1. Configure Markus’ backends using `markus.configure()`.
2. For each Python module or class or however you want to organize it, you use `markus.get_metrics()` to get a `markus.main.MetricsInterface`.
3. Use the various metrics reporting methods on the `markus.main.MetricsInterface`.

```python
import markus
from markus.filters import AddTagFilter

markus.configure([
    {
        "class": "markus.backends.logging.LoggingMetrics",
        "options": {
            "logger_name": "markus",
            "leader": "METRICS",
        }
    }
])
```

**[Filters](https://markus.readthedocs.io/en/latest/filters.html)** - Markus lets you write filters to modify generated metrics on the fly. This allows infinite customization to drop or modify metric values before they are emitted. Th

```python
class DebugFilter(MetricsFilter):
    def filter(self, record):
        if "debug:true" in record.tags:
            return
        return record
```

### Positive Consequences

* Quality of metrics customizations mean significant control of what metrics we want to emit.
* Built-in DogStatsD through backend.
* Lines up perfectly with our deployed infrastructure in Docker/Kubernetes (Telegraf & InfluxDB)
* High quality library and documentation mean an ease of development and maintenance.
* Backend configuration and filters mean fine-tuning of our metrics.
* Fast development time for minimal use cases.

### Negative Consequences

* None that come to mind, there are other viable alternatives but Markus seems to fit our needs very well.
* Possibly that Markus is a new and different library from say aiodogstatsd, which is used in Merino. However, that is an async library and it has several drabacks compared to Markus for our use case.


## Pros and Cons of the Options

### Markus
[Docs](https://markus.readthedocs.io/en/latest/)

[pypi](https://pypi.org/project/markus/)

[GitHub Repo](https://github.com/willkg/markus)

#### Pros

* Used by several teams managing robust and large Django apps (fx-private-relay, mdn, etc)
* Very easy to use.
* Allows configuration of multiple backends to process metrics emissions. 
* Filters for individual metrics.
* Highly customizable. 
* Exceptional documentation with great examples.
* Included test class for mocking metrics emissions, backends and pre-built assertions. Excellent testing docs.
* Core maintainer a Mozillian (willkg)
* Active maintenance and support.

#### Cons

* Different from other used libraries
* Takes a little time to get up to speed, but still easy to understand.


### Prometheus
[Docs](https://prometheus.io/)

[pypi](https://pypi.org/project/prometheus-client/)

[GitHub Repo](https://github.com/prometheus/client_python)

#### Pros

* Widely used in Django community.
* High quality documentation.
* A lot of possible customization, especially for Django.

#### Cons

* Some Mozillians advised against usage due to difficulty to set up and maintain.
* Cumbersome as you have to import each metric class individually to call.
* An open-source monitoring solution that we as an organization are not using. Some vertical integration needed to get full benefit.
* Supposedly some difficulty in configuring with our existing infrastructure.
* A little bit too complicated for our use case.

### statsd (pystatsd)
[Docs](https://statsd.readthedocs.io/en/latest/index.html)

[pypi](https://pypi.org/project/statsd/)

[GitHub Repo](https://github.com/jsocol/pystatsd)


#### Pros

* Excellent documentation.
* Good Django support and instructions for configuration.
* Active community and contribution.
* Basic, no frills.


#### Cons

* No testing framework, have to write totally custom tests without mocking or test classes built-in. 
* No provided backend configurations.
* A bit too simplistic and lacking in features.
* Somewhat cumbersome when dealing with specific customizations.



### aiodogstatsd 
[Docs](https://gr1n.github.io/aiodogstatsd/usage/)

[pypi](https://pypi.org/project/aiodogstatsd/)

[GitHub Repo](https://github.com/Gr1N/aiodogstatsd)

#### Pros

* Already used in Merino.
* Fairly self-evident implementation.


#### Cons

* Designed for asynchronous applications and Django is not an asynchronous app. Don't really require those features.
* Uses port 9125 by default and differs from the default StatsD implementation (can be modified, of course).
* Documentation is very scant, examples are limited.
* Does not include a test class or framework, test documentation nonexistent.
* Smaller team of maintainers and contributors. (last commit Dec 12, 2021).

## Links

* [Collecting Metrics Using StatsD, a Standard for Real-Time Monitoring ](https://thenewstack.io/collecting-metrics-using-statsd-a-standard-for-real-time-monitoring/)
* [Statsd - Original Protocol GitHub](https://github.com/statsd)
* [DogStatsD](https://docs.datadoghq.com/developers/dogstatsd/?tab=hostagent)
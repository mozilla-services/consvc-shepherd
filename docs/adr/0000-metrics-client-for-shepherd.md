# [short title of solved problem and solution]

* Status: accepted
* Deciders: taddes, tif, nan
* Date: 2023-05-30

## Context and Problem Statement

Shepherd is currently a simple Django Admin application used to create and publish snapshots and allocations of advertising partners.  The recent expansion of the service through the Project Honeycomb: Share-of-Voice epic [DISCO-2290] along with moving to a continuous deployment model [DISCO-2208] necessitated discussion around metrics and observability.  Up to this point, we did not have any information to analyze or

## Decision Drivers

1. Easy to implement, provides necessary features. Does not require excessive customization to Shepherd that hinders current/future development.
2. Has precident of effective usage - is used at Mozilla by other teams with more mature Django applcations.
3. Good documentation, easy testing (plus if testing/mocking framework provided), engagement and maintenance with broader community.

## Considered Options

* A. Markus
* B. Prometheus
* C. statsd (pystatsd)
* D. aiodogstatsd

## Decision Outcome

Chosen option:

* A. Markus

[justification. e.g., only option, which meets primary decision driver | which resolves a force or facing concern | … | comes out best (see below)].

### Positive Consequences

* [e.g., improvement of quality attribute satisfaction, follow-up decisions required, …]
* …

### Negative Consequences

* [e.g., compromising quality attribute, follow-up decisions required, …]
* …

## Pros and Cons of the Options

### Markus
[Docs](https://markus.readthedocs.io/en/latest/)
[Source](https://github.com/willkg/markus)
[example | description | pointer to more information | …]

#### Pros

* Used by several teams managing robust and large Django apps (fx-private-relay, mdn, etc)
* Very easy to use.
* Allows configuration of multiple backends to process metrics emissions. 
* Highly customizable. 
* Exceptional documentation with great examples.
* Included test class for mocking metrics emissions, backends and pre-built assertions. Excellent testing docs.
* Core maintainer a Mozillian (willkg)
* Active maintenance and 

#### Cons

* [argument against]

### Prometheus
[Docs](https://prometheus.io/)
[Source](https://github.com/prometheus/client_python)
[example | description | pointer to more information | …]

#### Pros

* [argument for]
* [argument for]


#### Cons

* Some Mozillians advised against usage due to difficulty to set up and maintain.
* An open-source monitoring solution that we as an organization are not using.

### statsd (pystatsd)
[Docs](https://statsd.readthedocs.io/en/latest/index.html)
[Source](https://github.com/jsocol/pystatsd)

[example | description | pointer to more information | …]

#### Pros

* [argument for]
* [argument for]


#### Cons

* [argument against]


### aiodogstatsd 
[Docs](https://gr1n.github.io/aiodogstatsd/usage/)
[Source](https://github.com/Gr1N/aiodogstatsd)
[example | description | pointer to more information | …]

#### Pros

* Already used in Merino.
* Simple to use


#### Cons

* Designed for asynchronous applications and Django is not an asynchronous app. Don't really require those features.
* Uses port 9125 by default and differs from the default StatsD implementations
* Documentation is rather scant, examples are limited
* Does not include a test class ir framework, test documentation
* Smaller team of maintainers and contributors. (last commit Dec 12, 2021) 

## Links

* 

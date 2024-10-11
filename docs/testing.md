# Test Strategy

Shepherd's test strategy involves ensuring that we do not go below a minimum unit test coverage percentage.

## Unit Tests

Unit tests are suitable for testing specific functional segments of code with fine-grained control over the inputs.
Due to their narrow scope, unit tests are fundamental for thorough test coverage.

A coverage report is printed to the shell showing the test results and possible exceptions. See [coverage.py docs](coverage-docs) for more details.

Unit tests are written and executed with `pytest` and are located in the test directories (i.e.`*/tests/`).

## Local Test Execution

To execute unit tests in the local Docker container, run: `make local-test`.

## Note on CI Test Execution

By default, unit tests run automatically in CI during each push to an active PR and during the merge process.
Check results in the [Shepherd CI Dashboard][shepherd-ci-dashboard].

## Testing a Django App

Django provides a number of tools, API methods, and classes to test web and Django-specific behavior.
These allow you to simulate requests, insert test data, and inspect your application's output.
See the most recent [Django test docs][django-test-docs] for reference. Also, see existing shepherd tests for examples.

[django-test-docs]: https://docs.djangoproject.com/en/4.2/topics/testing/tools/
[coverage-docs]: https://coverage.readthedocs.io/en/latest/
[shepherd-ci-dashboard]: https://app.circleci.com/pipelines/github/mozilla-services/consvc-shepherd

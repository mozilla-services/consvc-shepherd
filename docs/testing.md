# Test Strategy

Shepherd's test code is in the `consvc_shepherd/tests`, `contile/tests`, and `openidc/tests` directories.

## Unit Tests

The unit layer is suitable for testing complex behavior at a small scale, 
with fine-grained control over the inputs. 
Due to their narrow scope, unit tests are fundamental to thorough test coverage.

A coverage report is printed to the shell showing the test results and possible exceptions. See [coverage.py](https://coverage.readthedocs.io/en/latest/) for more details.

Unit tests are written and executed with `pytest` and are located in the test directories listed above, in the form: `*/tests/`. The name of individual test files should match those of the files they are testing in the form `test*.py`.
Ex. `models.py` should be `test_models.py`. 

To execute unit tests, use: `make test`. By default, these tests run in CI during each push 
to an active PR and during the merge process.

## Testing a Django App

Django provides a number of tools, API methods, and classes to test web and Django-specific behavior.
These allow you to simulate requests, insert test data, and inspect your application's output.
See the most recent [Django test docs][django-test-docs] for reference. Also, see existing shepherd tests for examples.

[django-test-docs]: https://docs.djangoproject.com/en/4.2/topics/testing/tools/
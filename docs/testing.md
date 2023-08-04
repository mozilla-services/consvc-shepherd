# Test Strategy

Shepherd's test code is in the `consvc_shepherd/tests` directory.

## Unit Tests

The unit layer is suitable for testing complex behavior at a small scale, with
fine-grained control over the inputs. 
Due to their narrow scope, unit tests are fundamental to thorough test coverage.

Our test coverage minimum is set to 95%.

To execute unit tests, use: `make unit-tests`

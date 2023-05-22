"""Unit tests for the version.py utility module."""
import json
import pathlib

import pytest

from consvc_shepherd.version import Version, fetch_app_version_from_file


def test_fetch_app_version_from_file() -> None:
    """Happy path test for fetch_app_version_from_file()."""
    expected_information = {
        "source": "https://github.com/mozilla-services/consvc-shepherd",
        "version": "dev",
        "commit": "TBD",
        "build": "TBD",
    }

    version = fetch_app_version_from_file()
    assert version == Version(**expected_information)


def test_fetch_app_version_from_file_invalid_path() -> None:
    """Test that the 'version.json' file cannot be read when provided
    an invalid path, raising a FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError) as excinfo:
        fetch_app_version_from_file(pathlib.Path("invalid"))

    assert "No such file or directory: 'invalid/version.json'" in str(excinfo.value)


@pytest.fixture(name="dir_containing_incorrect_file")
def fixture_dir_containing_incorrect_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create a version.json file that does not match the Version model."""
    version_file = tmp_path / "version.json"
    version_file.write_text(
        json.dumps(
            {
                "source": "https://github.com/mozilla-services/consvc-shepherd",
                "version": "dev",
                "commit": "TBD",
                "build": "TBD",
                "incorrect": "this should not be here",
            }
        )
    )
    return tmp_path

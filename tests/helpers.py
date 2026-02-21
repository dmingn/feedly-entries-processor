"""Shared test helpers."""

from unittest.mock import MagicMock

from requests.exceptions import HTTPError


def make_http_error(status_code: int) -> HTTPError:
    """Build an HTTPError with the given status code for retry tests."""
    error = HTTPError("Server error")
    error.response = MagicMock()
    error.response.status_code = status_code
    return error

"""Tests for the LogAction."""

from typing import Literal
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from feedly_entries_processor.actions.log_action import LogAction
from feedly_entries_processor.feedly_client import Entry


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mock the logzero logger."""
    return mocker.patch("feedly_entries_processor.actions.log_action.logger")


@pytest.fixture
def mock_entry() -> Entry:
    """Provide a mock Entry object."""
    return Entry(
        id="entry_id",
        title="Test Entry Title",
        canonical_url="http://example.com/entry",
    )


def test_log_action_instantiation() -> None:
    """Test that LogAction can be instantiated correctly."""
    action = LogAction(level="info")
    assert isinstance(action, LogAction)
    assert action.action_name == "log"
    assert action.level == "info"


def test_log_action_default_level() -> None:
    """Test that LogAction defaults to 'info' level."""
    action = LogAction()
    assert action.level == "info"


@pytest.mark.parametrize(
    ("level", "expected_log_method"),
    [
        ("info", "info"),
        ("debug", "debug"),
        ("warning", "warning"),
        ("error", "error"),
    ],
)
def test_log_action_process(
    level: Literal["info", "debug", "warning", "error"],
    expected_log_method: str,
    mock_logger: MagicMock,
    mock_entry: Entry,
) -> None:
    """Test that process logs at the correct level."""
    action = LogAction(level=level)
    action.process(mock_entry)

    log_message = (
        f"Processing entry: {mock_entry.title} (URL: {mock_entry.canonical_url})"
    )

    if expected_log_method == "info":
        mock_logger.info.assert_called_once_with(log_message)
    elif expected_log_method == "debug":
        mock_logger.debug.assert_called_once_with(log_message)
    elif expected_log_method == "warning":
        mock_logger.warning.assert_called_once_with(log_message)
    elif expected_log_method == "error":
        mock_logger.error.assert_called_once_with(log_message)
    else:
        pytest.fail(f"Unexpected log level: {level}")


def test_log_action_validation_error_invalid_level() -> None:
    """Test that ValidationError is raised for an invalid log level."""
    with pytest.raises(ValidationError):
        LogAction(level="invalid")  # type: ignore[arg-type, unused-ignore]

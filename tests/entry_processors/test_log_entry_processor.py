"""Tests for the LogEntryProcessor."""

from typing import Literal
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from feedly_entries_processor.entry_processors.log_entry_processor import (
    LogEntryProcessor,
)
from feedly_entries_processor.feedly_client import Entry


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mock the logzero logger."""
    return mocker.patch(
        "feedly_entries_processor.entry_processors.log_entry_processor.logger"
    )


@pytest.fixture
def mock_entry() -> Entry:
    """Provide a mock Entry object."""
    return Entry(
        id="entry_id",
        title="Test Entry Title",
        canonical_url="http://example.com/entry",
    )


def test_log_entry_processor_instantiation() -> None:
    """Test that LogEntryProcessor can be instantiated correctly."""
    processor = LogEntryProcessor(level="info")
    assert isinstance(processor, LogEntryProcessor)
    assert processor.processor_name == "log"
    assert processor.level == "info"


def test_log_entry_processor_default_level() -> None:
    """Test that LogEntryProcessor defaults to 'info' level."""
    processor = LogEntryProcessor()
    assert processor.level == "info"


@pytest.mark.parametrize(
    ("level", "expected_log_method"),
    [
        ("info", "info"),
        ("debug", "debug"),
        ("warning", "warning"),
        ("error", "error"),
    ],
)
def test_log_entry_processor_process_entry(
    level: Literal["info", "debug", "warning", "error"],
    expected_log_method: str,
    mock_logger: MagicMock,
    mock_entry: Entry,
) -> None:
    """Test that process_entry logs at the correct level."""
    processor = LogEntryProcessor(level=level)
    processor.process_entry(mock_entry)

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


def test_log_entry_processor_validation_error_invalid_level() -> None:
    """Test that ValidationError is raised for an invalid log level."""
    with pytest.raises(ValidationError):
        LogEntryProcessor(level="invalid")  # type: ignore[arg-type, unused-ignore]

"""Tests for the process module."""

from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from feedly_entries_processor.config_loader import Rule
from feedly_entries_processor.entry_processors import LogEntryProcessor
from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.matchers import AllMatcher
from feedly_entries_processor.process import process_entries, process_entry
from feedly_entries_processor.sources import SavedSource


@pytest.fixture
def mock_entry() -> Entry:
    """Fixture for a mock Entry."""
    return Entry(
        id="entry1",
        title="Test Entry",
        canonical_url="http://example.com/entry1",
        published=1234567890,
    )


@pytest.fixture
def mock_matcher(mocker: MockerFixture) -> AllMatcher:
    """Fixture for a mock AllMatcher."""
    mock = mocker.create_autospec(AllMatcher)
    mock.matcher_name = "all"
    return mock


@pytest.fixture
def mock_processor(mocker: MockerFixture) -> LogEntryProcessor:
    """Fixture for a mock LogEntryProcessor."""
    mock = mocker.create_autospec(LogEntryProcessor)
    mock.processor_name = "log"
    return mock


@pytest.fixture
def mock_rule(mock_matcher: AllMatcher, mock_processor: LogEntryProcessor) -> Rule:
    """Fixture for a mock Rule."""
    return Rule(
        name="test-rule",
        source=SavedSource(),
        match=mock_matcher,
        processor=mock_processor,
    )


def test_process_entry_calls_processor_when_rule_matches(
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry calls the processor when the rule matches."""
    cast("MagicMock", mock_rule.match).is_match.return_value = True

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.match).is_match.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.processor).process_entry.assert_called_once_with(
        mock_entry
    )


def test_process_entry_does_not_call_processor_when_rule_does_not_match(
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry does not call the processor when the rule does not match."""
    cast("MagicMock", mock_rule.match).is_match.return_value = False

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.match).is_match.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.processor).process_entry.assert_not_called()


def test_process_entry_handles_exception_in_is_match(
    mocker: MockerFixture,
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry handles exceptions raised by is_match."""
    cast("MagicMock", mock_rule.match).is_match.side_effect = Exception(
        "Test exception"
    )
    mock_logger_exception = mocker.patch(
        "feedly_entries_processor.process.logger.exception"
    )

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.match).is_match.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.processor).process_entry.assert_not_called()
    mock_logger_exception.assert_called_once()


def test_process_entry_handles_exception_in_processor(
    mocker: MockerFixture,
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry handles exceptions raised by the processor."""
    cast("MagicMock", mock_rule.match).is_match.return_value = True
    cast("MagicMock", mock_rule.processor).process_entry.side_effect = Exception(
        "Test exception"
    )
    mock_logger_exception = mocker.patch(
        "feedly_entries_processor.process.logger.exception"
    )

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.match).is_match.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.processor).process_entry.assert_called_once_with(
        mock_entry
    )
    mock_logger_exception.assert_called_once()


def test_process_entries_calls_process_entry_for_each_entry_and_rule(
    mocker: MockerFixture,
) -> None:
    """Test that process_entries calls process_entry for each entry and rule."""
    mock_process_entry = mocker.patch("feedly_entries_processor.process.process_entry")
    entry1, entry2 = MagicMock(spec=Entry), MagicMock(spec=Entry)
    rule1, rule2 = MagicMock(spec=Rule), MagicMock(spec=Rule)
    entries = [entry1, entry2]
    rules = [rule1, rule2]

    process_entries(entries, rules)

    expected_calls = [
        mocker.call(entry1, rule1),
        mocker.call(entry1, rule2),
        mocker.call(entry2, rule1),
        mocker.call(entry2, rule2),
    ]
    assert mock_process_entry.call_args_list == expected_calls

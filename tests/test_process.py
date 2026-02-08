"""Tests for the process module."""

from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from feedly_entries_processor.actions import LogAction
from feedly_entries_processor.conditions import MatchAllCondition
from feedly_entries_processor.config_loader import Rule
from feedly_entries_processor.feedly_client import Entry
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
def mock_condition(mocker: MockerFixture) -> MatchAllCondition:
    """Fixture for a mock MatchAllCondition."""
    mock = mocker.create_autospec(MatchAllCondition)
    mock.name = "match_all"
    return mock


@pytest.fixture
def mock_action(mocker: MockerFixture) -> LogAction:
    """Fixture for a mock LogAction."""
    mock = mocker.create_autospec(LogAction)
    mock.name = "log"
    return mock


@pytest.fixture
def mock_rule(mock_condition: MatchAllCondition, mock_action: LogAction) -> Rule:
    """Fixture for a mock Rule."""
    return Rule(
        name="test-rule",
        source=SavedSource(),
        condition=mock_condition,
        action=mock_action,
    )


def test_process_entry_calls_action_when_rule_matches(
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry calls the action when the rule matches."""
    cast("MagicMock", mock_rule.condition).matches.return_value = True

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.condition).matches.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.action).process.assert_called_once_with(mock_entry)


def test_process_entry_does_not_call_action_when_rule_does_not_match(
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry does not call the action when the rule does not match."""
    cast("MagicMock", mock_rule.condition).matches.return_value = False

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.condition).matches.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.action).process.assert_not_called()


def test_process_entry_handles_exception_in_matches(
    mocker: MockerFixture,
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry handles exceptions raised by matches."""
    cast("MagicMock", mock_rule.condition).matches.side_effect = Exception(
        "Test exception"
    )
    mock_logger_exception = mocker.patch(
        "feedly_entries_processor.process.logger.exception"
    )

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.condition).matches.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.action).process.assert_not_called()
    mock_logger_exception.assert_called_once()


def test_process_entry_handles_exception_in_action(
    mocker: MockerFixture,
    mock_entry: Entry,
    mock_rule: Rule,
) -> None:
    """Test that process_entry handles exceptions raised by the action."""
    cast("MagicMock", mock_rule.condition).matches.return_value = True
    cast("MagicMock", mock_rule.action).process.side_effect = Exception(
        "Test exception"
    )
    mock_logger_exception = mocker.patch(
        "feedly_entries_processor.process.logger.exception"
    )

    process_entry(mock_entry, mock_rule)

    cast("MagicMock", mock_rule.condition).matches.assert_called_once_with(mock_entry)
    cast("MagicMock", mock_rule.action).process.assert_called_once_with(mock_entry)
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

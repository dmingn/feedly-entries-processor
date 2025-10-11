"""Tests for the __main__ module."""

import json
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from feedly_entries_processor.__main__ import app, process_entries, process_entry
from feedly_entries_processor.config_loader import Config, Rule
from feedly_entries_processor.entry_processors.log_entry_processor import (
    LogEntryProcessor,
)
from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.rule_matcher import AllMatcher

runner = CliRunner()


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
        name="test-rule", source="saved", match=mock_matcher, processor=mock_processor
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
    mock_logger_exception = mocker.patch("logzero.logger.exception")

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
    mock_logger_exception = mocker.patch("logzero.logger.exception")

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
    mock_process_entry = mocker.patch("feedly_entries_processor.__main__.process_entry")
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


@pytest.fixture
def mock_load_config_file(mocker: MockerFixture, mock_rule: Rule) -> MagicMock:
    """Fixture to mock load_config."""
    config = Config(rules=frozenset({mock_rule}))
    return mocker.patch(
        "feedly_entries_processor.__main__.load_config_file", return_value=config
    )


@pytest.fixture
def mock_feedly_client(mocker: MockerFixture, mock_entry: Entry) -> MagicMock:
    """Fixture to mock FeedlyClient."""
    mock_client = mocker.MagicMock()
    mock_client.fetch_saved_entries.return_value = [mock_entry]
    return mocker.patch(
        "feedly_entries_processor.__main__.FeedlyClient",
        return_value=mock_client,
    )


@pytest.mark.usefixtures("mock_feedly_client")
def test_process_command(
    mocker: MockerFixture,
    tmp_path: Path,
    mock_entry: Entry,
    mock_load_config_file: MagicMock,
) -> None:
    """Test the process command."""
    mocker.patch("feedly_entries_processor.__main__.FileAuthStore")
    mocker.patch("feedly_entries_processor.__main__.FeedlySession")
    mock_process_entries = mocker.patch(
        "feedly_entries_processor.__main__.process_entries"
    )

    config_file = tmp_path / "config.yml"
    config_file.touch()
    token_dir = tmp_path / "tokens"
    token_dir.mkdir()

    result = runner.invoke(
        app,
        [
            "process",
            "--config-file",
            str(config_file),
            "--token-dir",
            str(token_dir),
        ],
    )

    assert result.exit_code == 0, result.output

    mock_load_config_file.assert_called_once_with(config_file)
    mock_config = mock_load_config_file.return_value
    mock_process_entries.assert_called_once_with(
        entries=[mock_entry], rules=mock_config.rules
    )


def test_show_config_schema_command() -> None:
    """Test the show-config-schema command."""
    result = runner.invoke(app, ["show-config-schema"])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == Config.model_json_schema()

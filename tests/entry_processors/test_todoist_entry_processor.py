"""Tests for the TodoistEntryProcessor."""

import datetime
from collections.abc import Callable
from typing import Literal
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from feedly_saved_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)
from feedly_saved_entries_processor.feedly_client import Entry, Origin, Summary


@pytest.fixture
def mock_todoist_api(mocker: MockerFixture) -> MagicMock:
    """Fixture for mocking TodoistAPI."""
    mock_api: MagicMock = mocker.patch(
        "feedly_saved_entries_processor.entry_processors.todoist_entry_processor.TodoistAPI"
    )
    return mock_api


@pytest.fixture
def todoist_processor(mocker: MockerFixture) -> Callable[..., TodoistEntryProcessor]:
    """Fixture for TodoistEntryProcessor factory."""
    mocker.patch.dict("os.environ", {"TODOIST_API_TOKEN": "test_token"})
    project_id = "test_project_id"

    def _factory(
        due_datetime: datetime.datetime | None = None,
        priority: Literal[1, 2, 3, 4] | None = None,
    ) -> TodoistEntryProcessor:
        return TodoistEntryProcessor(
            project_id=project_id, due_datetime=due_datetime, priority=priority
        )

    return _factory


@pytest.fixture
def entry_builder() -> Callable[..., Entry]:
    """Fixture for a builder function to create Entry objects."""

    def _builder(
        title: str = "Test Entry",
        canonical_url: str | None = "http://example.com/test",
        summary_content: str | None = "Test Summary Content",
    ) -> Entry:
        return Entry(
            id="test_id",
            title=title,
            canonical_url=canonical_url,
            origin=Origin(
                title="Test Origin",
                html_url="http://example.com",
                stream_id="test_stream_id",
            ),
            summary=Summary(content=summary_content) if summary_content else None,
            published=1234567890,
            author=None,
        )

    return _builder


def test_post_init(
    mock_todoist_api: MagicMock, todoist_processor: Callable[..., TodoistEntryProcessor]
) -> None:
    """Test that the Todoist API client is initialized correctly."""
    processor = todoist_processor()
    assert processor.todoist_client is not None
    assert processor.todoist_client == mock_todoist_api.return_value


def test_process_entry_success(
    mock_todoist_api: MagicMock,
    todoist_processor: Callable[..., TodoistEntryProcessor],
    entry_builder: Callable[..., Entry],
) -> None:
    """Test successful processing of an entry."""
    sample_entry = entry_builder()
    processor = todoist_processor()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_123"
    mock_instance.add_task.return_value.content = "Test Task"

    processor.process_entry(sample_entry)

    expected_content = "Test Entry - http://example.com/test"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=processor.project_id,
        priority=None,
        due_datetime=None,
        description="Test Summary Content",
    )


def test_process_entry_no_canonical_url(
    todoist_processor: Callable[..., TodoistEntryProcessor],
    entry_builder: Callable[..., Entry],
) -> None:
    """Test processing of an entry without a canonical URL raises an error."""
    entry = entry_builder(
        canonical_url=None, title="Test Entry No URL", summary_content=None
    )
    processor = todoist_processor()

    with pytest.raises(
        ValueError,
        match="Entry must have a canonical_url to be processed by TodoistEntryProcessor.",
    ):
        processor.process_entry(entry)


def test_process_entry_add_task_failure(
    mock_todoist_api: MagicMock,
    todoist_processor: Callable[..., TodoistEntryProcessor],
    entry_builder: Callable[..., Entry],
) -> None:
    """Test error handling when adding a task fails."""
    sample_entry = entry_builder()
    processor = todoist_processor()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        processor.process_entry(sample_entry)

    mock_instance.add_task.assert_called_once()


def test_process_entry_with_optional_params(
    mock_todoist_api: MagicMock,
    entry_builder: Callable[..., Entry],
    todoist_processor: Callable[..., TodoistEntryProcessor],  # Use the factory
) -> None:
    """Test processing of an entry with optional parameters (due_datetime, priority)."""
    due_datetime = datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
    priority: Literal[1, 2, 3, 4] = 2  # Use Literal for type hint

    # Create a new processor instance with the desired optional parameters using the factory
    processor_with_params = todoist_processor(
        due_datetime=due_datetime, priority=priority
    )

    entry = entry_builder(
        title="Entry with Params",
        canonical_url="http://example.com/params",
        summary_content="Summary for params",
    )
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_789"
    mock_instance.add_task.return_value.content = "Test Task with Params"

    processor_with_params.process_entry(entry)

    expected_content = "Entry with Params - http://example.com/params"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=processor_with_params.project_id,
        priority=priority,
        due_datetime=due_datetime,
        description="Summary for params",
    )

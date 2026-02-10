"""Tests for the AddTodoistTaskAction."""

import datetime
from collections.abc import Callable
from typing import Literal
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from feedly_entries_processor.actions.add_todoist_task_action import (
    AddTodoistTaskAction,
)
from feedly_entries_processor.feedly_client import Entry, Origin, Summary


@pytest.fixture
def mock_todoist_api(mocker: MockerFixture) -> MagicMock:
    """Fixture for mocking TodoistAPI."""
    mock_api: MagicMock = mocker.patch(
        "feedly_entries_processor.actions.add_todoist_task_action.TodoistAPI"
    )
    return mock_api


@pytest.fixture
def add_todoist_task_action_factory(
    mocker: MockerFixture,
) -> Callable[..., AddTodoistTaskAction]:
    """Fixture for AddTodoistTaskAction factory."""
    mocker.patch.dict("os.environ", {"TODOIST_API_TOKEN": "test_token"})
    project_id = "test_project_id"

    def _factory(
        due_datetime: datetime.datetime | None = None,
        priority: Literal[1, 2, 3, 4] | None = None,
    ) -> AddTodoistTaskAction:
        return AddTodoistTaskAction(
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


def test_AddTodoistTaskAction_initializes_todoist_client_on_first_access(
    mock_todoist_api: MagicMock,
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
) -> None:
    """Test that the Todoist API client is initialized and cached on first access."""
    # arrange
    action = add_todoist_task_action_factory()

    # assert
    assert action._todoist_client is not None  # noqa: SLF001
    assert action._todoist_client == mock_todoist_api.return_value  # noqa: SLF001


def test_AddTodoistTaskAction_process_creates_task_for_entry(
    mock_todoist_api: MagicMock,
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
) -> None:
    """Test successful processing of an entry."""
    # arrange
    sample_entry = entry_builder()
    action = add_todoist_task_action_factory()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_123"
    mock_instance.add_task.return_value.content = "Test Task"

    # act
    action.process(sample_entry)

    # assert
    expected_content = "Test Entry - http://example.com/test"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=action.project_id,
        priority=None,
        due_datetime=None,
        description="Test Summary Content",
    )


def test_AddTodoistTaskAction_process_raises_ValueError_for_entry_without_canonical_url(
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
) -> None:
    """Test processing of an entry without a canonical URL raises an error."""
    # arrange
    entry = entry_builder(
        canonical_url=None, title="Test Entry No URL", summary_content=None
    )
    action = add_todoist_task_action_factory()

    # act & assert
    with pytest.raises(
        ValueError,
        match=r"Entry must have a canonical_url to be processed by AddTodoistTaskAction\.",
    ):
        action.process(entry)


def test_AddTodoistTaskAction_process_raises_error_when_add_task_fails(
    mock_todoist_api: MagicMock,
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
) -> None:
    """Test error handling when adding a task fails."""
    # arrange
    sample_entry = entry_builder()
    action = add_todoist_task_action_factory()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.side_effect = Exception("API Error")

    # act & assert
    with pytest.raises(Exception, match="API Error"):
        action.process(sample_entry)

    mock_instance.add_task.assert_called_once()


def test_AddTodoistTaskAction_process_uses_optional_params_when_provided(
    mock_todoist_api: MagicMock,
    entry_builder: Callable[..., Entry],
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
) -> None:
    """Test processing of an entry with optional parameters (due_datetime, priority)."""
    # arrange
    due_datetime = datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
    priority: Literal[1, 2, 3, 4] = 2  # Use Literal for type hint

    action_with_params = add_todoist_task_action_factory(
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

    # act
    action_with_params.process(entry)

    # assert
    expected_content = "Entry with Params - http://example.com/params"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=action_with_params.project_id,
        priority=priority,
        due_datetime=due_datetime,
        description="Summary for params",
    )

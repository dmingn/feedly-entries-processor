"""Tests for the AddTodoistTaskAction."""

from collections.abc import Callable
from typing import Literal
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr
from pytest_mock import MockerFixture
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError

from feedly_entries_processor.actions.add_todoist_task_action import (
    AddTodoistTaskAction,
)
from feedly_entries_processor.exceptions import TodoistApiError
from feedly_entries_processor.feedly_client import Entry, Origin, Summary
from feedly_entries_processor.settings import TodoistSettings


@pytest.fixture
def mock_todoist_api(mocker: MockerFixture) -> MagicMock:
    """Fixture for mocking TodoistAPI."""
    mock_api: MagicMock = mocker.patch(
        "feedly_entries_processor.actions.add_todoist_task_action.TodoistAPI"
    )
    return mock_api


@pytest.fixture
def add_todoist_task_action_factory() -> Callable[..., AddTodoistTaskAction]:
    """Fixture for AddTodoistTaskAction factory."""
    project_id = "test_project_id"

    def _factory(
        due_string: str | None = None,
        priority: Literal[1, 2, 3, 4] | None = None,
        labels: frozenset[str] | None = None,
    ) -> AddTodoistTaskAction:
        return AddTodoistTaskAction(
            project_id=project_id,
            due_string=due_string,
            priority=priority,
            labels=labels,
            todoist_settings=TodoistSettings.model_construct(
                todoist_api_token=SecretStr("test_token")
            ),
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


def _make_http_error(status_code: int) -> HTTPError:
    """Build an HTTPError with the given status code for retry tests."""
    error = HTTPError("Server error")
    error.response = MagicMock()
    error.response.status_code = status_code
    return error


def test_AddTodoistTaskAction_process_creates_task_without_optional_params(
    mock_todoist_api: MagicMock,
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
) -> None:
    # arrange
    sample_entry = entry_builder()
    action = add_todoist_task_action_factory()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_123"
    mock_instance.add_task.return_value.content = "Test Task"

    # act
    action.process(sample_entry)

    # assert
    mock_instance.add_task.assert_called_once_with(
        content="Test Entry - http://example.com/test",
        project_id=action.project_id,
        description="Test Summary Content",
        priority=None,
        due_string=None,
        labels=None,
    )


def test_AddTodoistTaskAction_process_creates_task_with_all_optional_params(
    mock_todoist_api: MagicMock,
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
) -> None:
    # arrange
    due_string = "today"
    priority: Literal[1, 2, 3, 4] = 2
    labels = frozenset({"reading"})

    action_with_params = add_todoist_task_action_factory(
        due_string=due_string, priority=priority, labels=labels
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
    mock_instance.add_task.assert_called_once_with(
        content="Entry with Params - http://example.com/params",
        project_id=action_with_params.project_id,
        description="Summary for params",
        priority=priority,
        due_string=due_string,
        labels=["reading"],
    )


def test_AddTodoistTaskAction_process_raises_ValueError_when_todoist_api_token_is_not_set(
    entry_builder: Callable[..., Entry],
) -> None:
    # arrange: action with no token
    action = AddTodoistTaskAction(
        project_id="test_project_id",
        todoist_settings=TodoistSettings.model_construct(todoist_api_token=None),
    )
    entry = entry_builder()

    # act & assert
    with pytest.raises(
        ValueError,
        match=r"TODOIST_API_TOKEN must be set",
    ):
        action.process(entry)


def test_AddTodoistTaskAction_process_raises_ValueError_for_entry_without_canonical_url(
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
) -> None:
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
    # arrange
    sample_entry = entry_builder()
    action = add_todoist_task_action_factory()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.side_effect = Exception("API Error")

    # act & assert
    with pytest.raises(Exception, match="API Error"):
        action.process(sample_entry)

    mock_instance.add_task.assert_called_once()


@pytest.mark.parametrize(
    "request_exception",
    [
        _make_http_error(400),
        RequestsConnectionError("Connection failed"),
    ],
)
def test_AddTodoistTaskAction_process_raises_TodoistApiError_on_RequestException(
    mock_todoist_api: MagicMock,
    add_todoist_task_action_factory: Callable[..., AddTodoistTaskAction],
    entry_builder: Callable[..., Entry],
    request_exception: Exception,
) -> None:
    # arrange
    sample_entry = entry_builder()
    action = add_todoist_task_action_factory()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.side_effect = request_exception

    # act & assert
    with pytest.raises(TodoistApiError) as exc_info:
        action.process(sample_entry)

    assert "Todoist API request failed" in exc_info.value.args[0]
    assert exc_info.value.details["project_id"] == action.project_id
    # HTTPError (e.g. 400) is not retried; ConnectionError is retried 3 times
    assert mock_instance.add_task.call_count >= 1

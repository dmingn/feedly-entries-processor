"""Tests for persistent error skipping in AddTodoistTaskAction."""

import pytest
from pydantic import SecretStr
from pytest_mock import MockerFixture
from requests import Response
from requests.exceptions import HTTPError

from feedly_entries_processor.actions.add_todoist_task_action import (
    AddTodoistTaskAction,
)
from feedly_entries_processor.exceptions import (
    ActionSkippedDueToPersistentError,
    TodoistApiError,
)
from feedly_entries_processor.feedly_client import Entry, Origin
from feedly_entries_processor.settings import TodoistSettings


@pytest.fixture
def entry() -> Entry:
    return Entry(
        id="test_id",
        title="Test Entry",
        canonical_url="http://example.com",
        origin=Origin(title="o", html_url="h", stream_id="s"),
        published=123,
    )


@pytest.fixture
def todoist_action() -> AddTodoistTaskAction:
    return AddTodoistTaskAction(
        project_id="p123",
        todoist_settings=TodoistSettings.model_construct(
            todoist_api_token=SecretStr("test_token")
        ),
    )


def test_AddTodoistTaskAction_skips_after_403(
    mocker: MockerFixture,
    todoist_action: AddTodoistTaskAction,
    entry: Entry,
) -> None:
    # 1. Mock TodoistAPI to raise a 403 error
    mock_api_class = mocker.patch(
        "feedly_entries_processor.actions.add_todoist_task_action.TodoistAPI"
    )
    mock_api = mock_api_class.return_value

    response = Response()
    response.status_code = 403
    mock_api.add_task.side_effect = HTTPError(response=response)

    # 2. First call should raise TodoistApiError (403)
    with pytest.raises(TodoistApiError) as exc_info:
        todoist_action.process(entry)
    assert exc_info.value.details["status_code"] == 403

    # 3. Subsequent call should raise ActionSkippedDueToPersistentError
    with pytest.raises(ActionSkippedDueToPersistentError) as exc_info_skip:
        todoist_action.process(entry)

    assert "persistent error occurred previously" in str(exc_info_skip.value)
    assert mock_api.add_task.call_count == 1  # Only called once


def test_AddTodoistTaskAction_does_not_skip_after_500(
    mocker: MockerFixture,
    todoist_action: AddTodoistTaskAction,
    entry: Entry,
) -> None:
    # 1. Mock TodoistAPI to raise a 500 error
    mock_api_class = mocker.patch(
        "feedly_entries_processor.actions.add_todoist_task_action.TodoistAPI"
    )
    mock_api = mock_api_class.return_value

    response = Response()
    response.status_code = 500
    mock_api.add_task.side_effect = HTTPError(response=response)

    # 2. First call should raise TodoistApiError (500)
    # Note: add_task_with_retry will retry 3 times for 500
    with pytest.raises(TodoistApiError) as exc_info:
        todoist_action.process(entry)
    assert exc_info.value.details["status_code"] == 500

    # 3. Subsequent call should NOT raise ActionSkippedDueToPersistentError but TodoistApiError again
    with pytest.raises(TodoistApiError) as exc_info_retry:
        todoist_action.process(entry)
    assert exc_info_retry.value.details["status_code"] == 500

    # Total calls: 3 (first process call) + 3 (second process call) = 6
    assert mock_api.add_task.call_count == 6

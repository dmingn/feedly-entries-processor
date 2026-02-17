"""Add Todoist task action."""

from typing import Literal

from logzero import logger
from pydantic import Field
from requests.exceptions import HTTPError, RequestException
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

from feedly_entries_processor.actions.base_action import BaseAction
from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.settings import TodoistSettings


def _should_retry_todoist_request(exc: BaseException) -> bool:
    """Return True if the exception is worth retrying (transient/rate limit)."""
    if isinstance(exc, RequestException) and not isinstance(exc, HTTPError):
        return True
    if isinstance(exc, HTTPError) and exc.response is not None:
        return exc.response.status_code in (429, 500, 502, 503, 504)
    return False


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception(_should_retry_todoist_request),
)
def _add_todoist_task_with_retry(  # noqa: PLR0913
    client: TodoistAPI,
    *,
    content: str,
    project_id: str,
    priority: Literal[1, 2, 3, 4] | None,
    due_string: str | None,
    description: str | None,
) -> Task:
    """Call Todoist add_task with retry on transient and rate-limit errors."""
    return client.add_task(
        content=content,
        project_id=project_id,
        priority=priority,
        due_string=due_string,
        description=description,
    )


class AddTodoistTaskAction(BaseAction):
    """An action that adds Feedly entries as tasks in Todoist."""

    name: Literal["add_todoist_task"] = "add_todoist_task"
    project_id: str
    due_string: str | None = None
    priority: Literal[1, 2, 3, 4] | None = None
    todoist_settings: TodoistSettings = Field(default_factory=TodoistSettings)

    def process(self, entry: Entry) -> None:
        """Process a Feedly entry by adding it as a task to Todoist."""
        if self.todoist_settings.todoist_api_token is None:
            error_message = "TODOIST_API_TOKEN must be set (e.g. via environment or .env) when using add_todoist_task action"
            raise ValueError(error_message)

        if entry.canonical_url is None:
            error_message = "Entry must have a canonical_url to be processed by AddTodoistTaskAction."
            raise ValueError(error_message)

        api_token = self.todoist_settings.todoist_api_token.get_secret_value()
        client = TodoistAPI(api_token)

        task_content = f"{entry.title} - {entry.canonical_url}"

        task = _add_todoist_task_with_retry(
            client,
            content=task_content,
            project_id=self.project_id,
            priority=self.priority,
            due_string=self.due_string,
            description=entry.summary.content if entry.summary else None,
        )

        logger.info(f"Added task to Todoist: {task.content} (ID: {task.id})")

"""Add Todoist task action."""

from typing import Literal

from logzero import logger
from pydantic import Field
from todoist_api_python.api import TodoistAPI

from feedly_entries_processor.actions.base_action import BaseAction
from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.settings import TodoistSettings


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

        task = client.add_task(
            content=task_content,
            project_id=self.project_id,
            priority=self.priority,
            due_string=self.due_string,
            description=entry.summary.content if entry.summary else None,
        )

        logger.info(f"Added task to Todoist: {task.content} (ID: {task.id})")

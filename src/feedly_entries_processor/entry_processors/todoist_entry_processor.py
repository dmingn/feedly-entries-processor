"""Todoist entry processor."""

import datetime
import os
from functools import cached_property
from typing import Literal

from logzero import logger
from todoist_api_python.api import TodoistAPI

from feedly_entries_processor.entry_processors.base_entry_processor import (
    BaseEntryProcessor,
)
from feedly_entries_processor.feedly_client import Entry


class TodoistEntryProcessor(BaseEntryProcessor):
    """A processor that saves Feedly entries as tasks in Todoist."""

    processor_name: Literal["todoist"] = "todoist"
    project_id: str
    due_datetime: datetime.datetime | None = None
    priority: Literal[1, 2, 3, 4] | None = None

    @cached_property
    def _todoist_client(self) -> TodoistAPI:
        """Initialize and cache the Todoist API client."""
        api_token = os.environ.get("TODOIST_API_TOKEN")
        if not api_token:
            error_message = "TODOIST_API_TOKEN environment variable must be set"
            raise ValueError(error_message)
        return TodoistAPI(api_token)

    def process_entry(self, entry: Entry) -> None:
        """Process a Feedly entry by adding it as a task to Todoist."""
        if entry.canonical_url is None:
            error_message = "Entry must have a canonical_url to be processed by TodoistEntryProcessor."
            raise ValueError(error_message)

        task_content = f"{entry.title} - {entry.canonical_url}"

        task = self._todoist_client.add_task(
            content=task_content,
            project_id=self.project_id,
            priority=self.priority,
            due_datetime=self.due_datetime,
            description=entry.summary.content if entry.summary else None,
        )

        logger.info(f"Added task to Todoist: {task.content} (ID: {task.id})")

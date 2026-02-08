"""Actions for Feedly entries."""

from feedly_entries_processor.actions.add_todoist_task_action import (
    AddTodoistTaskAction,
)
from feedly_entries_processor.actions.log_action import LogAction

__all__ = ["AddTodoistTaskAction", "LogAction"]

Action = LogAction | AddTodoistTaskAction

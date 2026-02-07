"""Actions for Feedly entries."""

from feedly_entries_processor.actions.log_action import LogAction
from feedly_entries_processor.actions.todoist_action import TodoistAction

__all__ = ["LogAction", "TodoistAction"]

Action = LogAction | TodoistAction

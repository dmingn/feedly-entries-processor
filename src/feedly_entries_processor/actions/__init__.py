"""Actions for Feedly entries."""

from feedly_entries_processor.actions.add_todoist_task_action import (
    AddTodoistTaskAction,
)
from feedly_entries_processor.actions.log_action import LogAction
from feedly_entries_processor.actions.remove_from_feedly_tag_action import (
    RemoveFromFeedlyTagAction,
)
from feedly_entries_processor.actions.run_sequence_action import RunSequenceAction

__all__ = [
    "AddTodoistTaskAction",
    "LogAction",
    "RemoveFromFeedlyTagAction",
    "RunSequenceAction",
]

Action = (
    LogAction | AddTodoistTaskAction | RemoveFromFeedlyTagAction | RunSequenceAction
)

RunSequenceAction.model_rebuild()

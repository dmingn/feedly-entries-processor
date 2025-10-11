"""Entry processors for Feedly entries."""

from feedly_entries_processor.entry_processors.log_entry_processor import (
    LogEntryProcessor,
)
from feedly_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)

__all__ = ["LogEntryProcessor", "TodoistEntryProcessor"]

EntryProcessor = LogEntryProcessor | TodoistEntryProcessor

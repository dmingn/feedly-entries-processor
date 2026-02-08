"""StreamIdInListCondition module."""

from typing import Literal

from feedly_entries_processor.conditions.base_condition import BaseCondition
from feedly_entries_processor.feedly_client import Entry


class StreamIdInListCondition(BaseCondition):
    """Condition that matches when stream_id is in a given list."""

    condition_name: Literal["stream_id_in_list"]
    stream_ids: tuple[str, ...]

    def is_match(self, entry: Entry) -> bool:
        """Check if the entry's stream_id is in the provided list."""
        return entry.origin is not None and entry.origin.stream_id in self.stream_ids

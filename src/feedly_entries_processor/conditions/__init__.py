"""Conditions for filtering Feedly entries."""

from feedly_entries_processor.conditions.match_all_condition import (
    MatchAllCondition,
)
from feedly_entries_processor.conditions.stream_id_in_list_condition import (
    StreamIdInListCondition,
)

__all__ = ["MatchAllCondition", "StreamIdInListCondition"]

Condition = MatchAllCondition | StreamIdInListCondition

"""Conditions for filtering Feedly entries."""

from feedly_entries_processor.conditions.all_condition import AllCondition
from feedly_entries_processor.conditions.stream_id_in_condition import (
    StreamIdInCondition,
)

__all__ = ["AllCondition", "StreamIdInCondition"]

Condition = AllCondition | StreamIdInCondition

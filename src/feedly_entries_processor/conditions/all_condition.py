"""AllCondition module."""

from typing import Literal

from feedly_entries_processor.conditions.base_condition import BaseCondition
from feedly_entries_processor.feedly_client import Entry


class AllCondition(BaseCondition):
    """Condition that matches all entries."""

    condition_name: Literal["all"]

    def is_match(self, entry: Entry) -> bool:  # noqa: ARG002
        """Check if the entry matches (always true for AllCondition)."""
        return True

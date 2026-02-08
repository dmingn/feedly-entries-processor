"""MatchAllCondition module."""

from typing import Literal

from feedly_entries_processor.conditions.base_condition import BaseCondition
from feedly_entries_processor.feedly_client import Entry


class MatchAllCondition(BaseCondition):
    """Condition that matches all entries."""

    condition_name: Literal["match_all"] = "match_all"

    def matches(self, entry: Entry) -> bool:  # noqa: ARG002
        """Return True (always true for MatchAllCondition)."""
        return True

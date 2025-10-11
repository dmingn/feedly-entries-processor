"""AllMatcher module."""

from typing import Literal

from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.matchers.base_matcher import BaseMatcher


class AllMatcher(BaseMatcher):
    """Matcher for all entries."""

    matcher_name: Literal["all"]

    def is_match(self, entry: Entry) -> bool:  # noqa: ARG002
        """Check if the entry matches (always true for AllMatcher)."""
        return True

"""StreamIdInMatcher module."""

from typing import Literal

from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.matchers.base_matcher import BaseMatcher


class StreamIdInMatcher(BaseMatcher):
    """Matcher for matching based on stream_id being in a list."""

    matcher_name: Literal["stream_id_in"]
    stream_ids: tuple[str, ...]

    def is_match(self, entry: Entry) -> bool:
        """Check if the entry's stream_id is in the provided list."""
        return entry.origin is not None and entry.origin.stream_id in self.stream_ids

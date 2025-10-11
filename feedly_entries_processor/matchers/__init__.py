"""Matchers for filtering Feedly entries."""

from feedly_entries_processor.matchers.all_matcher import AllMatcher
from feedly_entries_processor.matchers.stream_id_in_matcher import StreamIdInMatcher

__all__ = ["AllMatcher", "StreamIdInMatcher"]

Matcher = AllMatcher | StreamIdInMatcher

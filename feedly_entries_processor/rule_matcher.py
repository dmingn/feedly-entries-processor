"""Module for matching Feedly entries against defined rules."""

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, ConfigDict

from feedly_entries_processor.feedly_client import Entry


class BaseMatcher(ABC, BaseModel):
    """Base class for matching rules."""

    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def is_match(self, entry: Entry) -> bool:
        """Abstract method to check if an entry matches."""


class AllMatcher(BaseMatcher):
    """Matcher for all entries."""

    matcher_name: Literal["all"]

    def is_match(self, entry: Entry) -> bool:  # noqa: ARG002
        """Check if the entry matches (always true for AllStrategy)."""
        return True


class StreamIdInMatcher(BaseMatcher):
    """Matcher for matching based on stream_id being in a list."""

    matcher_name: Literal["stream_id_in"]
    stream_ids: tuple[str, ...]

    def is_match(self, entry: Entry) -> bool:
        """Check if the entry's stream_id is in the provided list."""
        return bool(entry.origin and entry.origin.stream_id in self.stream_ids)

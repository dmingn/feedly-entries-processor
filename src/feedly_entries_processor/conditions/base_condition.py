"""BaseMatcher module."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from feedly_entries_processor.feedly_client import Entry


class BaseMatcher(ABC, BaseModel):
    """Base class for matching rules."""

    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def is_match(self, entry: Entry) -> bool:
        """Abstract method to check if an entry matches."""

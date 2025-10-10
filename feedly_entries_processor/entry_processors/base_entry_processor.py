"""Base class for processing Feedly entries."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from feedly_entries_processor.feedly_client import Entry


class BaseEntryProcessor(ABC, BaseModel):
    """Base class for processing Feedly entries."""

    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def process_entry(self, entry: Entry) -> None:
        """Process a single Feedly entry."""

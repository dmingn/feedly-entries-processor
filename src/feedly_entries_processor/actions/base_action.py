"""Base class for rule actions."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from feedly_entries_processor.feedly_client import Entry


class BaseAction(ABC, BaseModel):
    """Base class for rule actions."""

    model_config = ConfigDict(frozen=True)

    @abstractmethod
    def process(self, entry: Entry) -> None:
        """Process a single Feedly entry."""

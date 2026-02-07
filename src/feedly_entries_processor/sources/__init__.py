"""Stream sources for fetching Feedly entries."""

from feedly_entries_processor.sources.all_source import AllSource
from feedly_entries_processor.sources.saved_source import SavedSource

__all__ = ["AllSource", "SavedSource", "StreamSource"]

StreamSource = SavedSource | AllSource

"""Stream sources for fetching Feedly entries."""

from feedly_entries_processor.sources.saved_source import SavedSource

__all__ = ["SavedSource", "StreamSource"]

StreamSource = SavedSource

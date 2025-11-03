"""Custom exceptions for the application."""


class FeedlyEntriesProcessorError(Exception):
    """Base exception for the application."""


class ConfigError(FeedlyEntriesProcessorError):
    """Raised when there is an error loading the configuration."""


class FeedlyClientInitError(FeedlyEntriesProcessorError):
    """Raised when there is an error initializing the Feedly client."""


class FetchEntriesError(FeedlyEntriesProcessorError):
    """Raised when there is an error fetching entries from Feedly."""

"""Custom exceptions for the application."""


class ConfigError(Exception):
    """Raised when there is an error loading the configuration."""


class FeedlyClientInitError(Exception):
    """Raised when there is an error initializing the Feedly client."""


class FetchEntriesError(Exception):
    """Raised when there is an error fetching entries from Feedly."""

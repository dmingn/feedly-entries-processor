"""Log entry processor."""

from typing import Literal, assert_never

from logzero import logger

from feedly_entries_processor.entry_processors.base_entry_processor import (
    BaseEntryProcessor,
)
from feedly_entries_processor.feedly_client import Entry


class LogEntryProcessor(BaseEntryProcessor):
    """A processor that only logs the Feedly entry."""

    processor_name: Literal["log"] = "log"
    level: Literal["info", "debug", "warning", "error"] = "info"

    def process_entry(self, entry: Entry) -> None:
        """Process a Feedly entry by logging its details."""
        log_message = f"Processing entry: {entry.title} (URL: {entry.canonical_url})"
        match self.level:
            case "info":
                logger.info(log_message)
            case "debug":
                logger.debug(log_message)
            case "warning":
                logger.warning(log_message)
            case "error":
                logger.error(log_message)
            case _ as unexpected_level:
                assert_never(unexpected_level)

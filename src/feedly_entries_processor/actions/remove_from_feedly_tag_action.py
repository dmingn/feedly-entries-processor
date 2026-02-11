"""Remove from Feedly tag action."""

import os
from functools import cached_property
from pathlib import Path
from typing import Annotated, Literal

from logzero import logger
from pydantic.types import StringConstraints

from feedly_entries_processor.actions.base_action import BaseAction
from feedly_entries_processor.feedly_client import (
    Entry,
    FeedlyClient,
    create_feedly_client,
)


class RemoveFromFeedlyTagAction(BaseAction):
    """An action that removes Feedly entries from a Feedly tag (e.g. saved)."""

    name: Literal["remove_from_feedly_tag"] = "remove_from_feedly_tag"
    tag: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    token_dir: Path | None = None

    @cached_property
    def _feedly_client(self) -> FeedlyClient:
        """Initialize and cache the Feedly API client."""
        return create_feedly_client(self._resolved_token_dir)

    @property
    def _resolved_token_dir(self) -> Path:
        """Return the token directory from config or environment."""
        if self.token_dir is not None:
            return self.token_dir
        return Path(os.environ.get("FEEDLY_TOKEN_DIR", "~/.config/feedly")).expanduser()

    def process(self, entry: Entry) -> None:
        """Process a Feedly entry by removing it from the configured tag."""
        self._feedly_client.remove_entry_from_tag(self.tag, entry.id)
        logger.info(
            f"Removed entry from Feedly tag: {entry.title!r} (entry ID: {entry.id})"
        )

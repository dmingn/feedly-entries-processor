"""Feedly client for fetching entries."""

from collections.abc import Generator
from pathlib import Path

from feedly.api_client.session import FeedlySession, FileAuthStore
from logzero import logger
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic.alias_generators import to_camel
from requests.exceptions import RequestException

from feedly_entries_processor.exceptions import (
    FeedlyClientInitError,
    FetchEntriesError,
)


class Summary(BaseModel):
    """Summary model."""

    content: str
    model_config = ConfigDict(
        alias_generator=to_camel,
        frozen=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class Origin(BaseModel):
    """Origin model."""

    html_url: str
    stream_id: str
    title: str
    model_config = ConfigDict(
        alias_generator=to_camel,
        frozen=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class Entry(BaseModel):
    """Entry model."""

    id: str
    author: str | None = None
    canonical_url: str | None = None
    origin: Origin | None = None
    published: int | None = None
    summary: Summary | None = None
    title: str | None = None
    model_config = ConfigDict(
        alias_generator=to_camel,
        frozen=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class StreamContents(BaseModel):
    """StreamContents model."""

    items: list[Entry]
    continuation: str | None = None
    model_config = ConfigDict(frozen=True)


class FeedlyClient:
    """Feedly client for fetching entries."""

    def __init__(self, feedly_session: FeedlySession) -> None:
        self.feedly_session = feedly_session

    @property
    def user_id(self) -> str:
        """Return the authenticated user's ID."""
        return str(self.feedly_session.user.id)

    def fetch_entries(self, stream_id: str) -> Generator[Entry]:
        """Fetch entries from a stream.

        Parameters
        ----------
            stream_id: The ID of the stream to fetch entries from.

        Yields
        ------
            An iterator of Entry objects.

        Raises
        ------
            FetchEntriesError: If there is an error fetching entries from Feedly.
        """
        continuation = None

        while True:
            logger.debug(
                f"Fetching entries from stream {stream_id} with continuation: {continuation}"
            )
            try:
                stream_contents = StreamContents.model_validate(
                    self.feedly_session.do_api_request(
                        relative_url="/v3/streams/contents",
                        params=(
                            {
                                "streamId": stream_id,
                                "count": "1000",
                                "ranked": "oldest",
                            }
                            | ({"continuation": continuation} if continuation else {})
                        ),
                    ),
                )
            except (RequestException, ValidationError) as e:
                msg = f"Failed to fetch entries from stream {stream_id}."
                raise FetchEntriesError(msg) from e

            logger.debug(f"Fetched {len(stream_contents.items)} entries.")

            yield from stream_contents.items

            if (not stream_contents.continuation) or (not stream_contents.items):
                logger.debug("No more entries to fetch or continuation is None.")
                break

            continuation = stream_contents.continuation


def create_feedly_client(token_dir: Path) -> FeedlyClient:
    """Create a Feedly client.

    Parameters
    ----------
    token_dir
        The directory where the Feedly API token is stored.

    Returns
    -------
    FeedlyClient
        An initialized Feedly client.

    Raises
    ------
    FeedlyClientInitError
        If there is an error initializing the Feedly client.
    """
    try:
        auth = FileAuthStore(token_dir=token_dir)
        feedly_session = FeedlySession(auth=auth)
        return FeedlyClient(feedly_session=feedly_session)
    except (ValueError, FileNotFoundError, PermissionError) as e:
        msg = (
            f"Failed to initialize Feedly client from token directory {token_dir}: {e}"
        )
        raise FeedlyClientInitError(msg) from e

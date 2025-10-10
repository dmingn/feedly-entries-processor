"""Feedly client for fetching saved entries."""

from collections.abc import Generator

from feedly.api_client.session import FeedlySession
from logzero import logger
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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
    """Feedly client for fetching saved entries."""

    def __init__(self, feedly_session: FeedlySession) -> None:
        self.feedly_session = feedly_session

    def fetch_entries(self, stream_id: str) -> Generator[Entry]:
        """Fetch entries from a stream."""
        continuation = None

        while True:
            logger.debug(
                f"Fetching entries from stream {stream_id} with continuation: {continuation}"
            )
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
            logger.debug(f"Fetched {len(stream_contents.items)} entries.")

            yield from stream_contents.items

            if (not stream_contents.continuation) or (not stream_contents.items):
                logger.debug("No more entries to fetch or continuation is None.")
                break

            continuation = stream_contents.continuation

    def fetch_saved_entries(self) -> Generator[Entry]:
        """Fetch saved entries from Feedly."""
        yield from self.fetch_entries(
            f"user/{self.feedly_session.user.id}/tag/global.saved"
        )

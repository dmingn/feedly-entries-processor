"""Tests for the Feedly client."""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture
from requests.exceptions import RequestException

from feedly_entries_processor.exceptions import FetchEntriesError
from feedly_entries_processor.feedly_client import Entry, FeedlyClient, Origin, Summary


@pytest.fixture
def mock_feedly_session() -> MagicMock:
    """Fixture for a mock FeedlySession."""
    session = MagicMock()
    session.user.id = "test_user_id"
    return session


def test_fetch_entries_single_page(mock_feedly_session: MagicMock) -> None:
    """Test fetching entries with a single page of results."""
    mock_feedly_session.do_api_request.return_value = {
        "items": [
            {
                "id": "entry1",
                "title": "Title 1",
                "author": "Author 1",
                "published": 1678886400000,
                "summary": {"content": "Summary 1"},
                "canonicalUrl": "http://example.com/canonical/1",
                "origin": {
                    "htmlUrl": "http://example.com/1",
                    "streamId": "stream1",
                    "title": "Origin 1",
                },
            },
            {
                "id": "entry2",
                "title": "Title 2",
                "author": "Author 2",
                "published": 1678886401000,
                "summary": {"content": "Summary 2"},
                "canonicalUrl": "http://example.com/canonical/2",
                "origin": {
                    "htmlUrl": "http://example.com/2",
                    "streamId": "stream2",
                    "title": "Origin 2",
                },
            },
        ],
        "continuation": None,  # No more pages
    }

    client = FeedlyClient(mock_feedly_session)
    stream_id = "dummy_stream_id"
    entries = list(client.fetch_entries(stream_id))

    expected_entries = [
        Entry(
            id="entry1",
            title="Title 1",
            author="Author 1",
            published=1678886400000,
            summary=Summary(content="Summary 1"),
            canonical_url="http://example.com/canonical/1",
            origin=Origin(
                html_url="http://example.com/1",
                stream_id="stream1",
                title="Origin 1",
            ),
        ),
        Entry(
            id="entry2",
            title="Title 2",
            author="Author 2",
            published=1678886401000,
            summary=Summary(content="Summary 2"),
            canonical_url="http://example.com/canonical/2",
            origin=Origin(
                html_url="http://example.com/2",
                stream_id="stream2",
                title="Origin 2",
            ),
        ),
    ]

    assert entries == expected_entries
    mock_feedly_session.do_api_request.assert_called_once_with(
        relative_url="/v3/streams/contents",
        params={
            "streamId": stream_id,
            "count": "1000",
            "ranked": "oldest",
        },
    )


def test_fetch_entries_multiple_pages(mock_feedly_session: MagicMock) -> None:
    """Test fetching entries with multiple pages of results."""
    mock_feedly_session.do_api_request.side_effect = [
        # First page
        {
            "items": [{"id": "entry1"}, {"id": "entry2"}],
            "continuation": "continuation1",
        },
        # Second page
        {
            "items": [{"id": "entry3"}, {"id": "entry4"}],
            "continuation": None,  # No more pages
        },
    ]

    client = FeedlyClient(mock_feedly_session)
    stream_id = "dummy_stream_id"
    entries = list(client.fetch_entries(stream_id))

    assert len(entries) == 4
    assert entries[0].id == "entry1"
    assert entries[1].id == "entry2"
    assert entries[2].id == "entry3"
    assert entries[3].id == "entry4"

    # Verify calls
    mock_feedly_session.do_api_request.assert_any_call(
        relative_url="/v3/streams/contents",
        params={
            "streamId": stream_id,
            "count": "1000",
            "ranked": "oldest",
        },
    )
    mock_feedly_session.do_api_request.assert_any_call(
        relative_url="/v3/streams/contents",
        params={
            "streamId": stream_id,
            "count": "1000",
            "ranked": "oldest",
            "continuation": "continuation1",
        },
    )
    assert mock_feedly_session.do_api_request.call_count == 2


def test_fetch_entries_no_entries(mock_feedly_session: MagicMock) -> None:
    """Test fetching entries when no entries are returned."""
    mock_feedly_session.do_api_request.return_value = {
        "items": [],
        "continuation": None,
    }

    client = FeedlyClient(mock_feedly_session)
    stream_id = "dummy_stream_id"
    entries = list(client.fetch_entries(stream_id))

    assert len(entries) == 0
    mock_feedly_session.do_api_request.assert_called_once()


def test_fetch_saved_entries_calls_fetch_entries(
    mock_feedly_session: MagicMock, mocker: MockerFixture
) -> None:
    """Test that fetch_saved_entries calls fetch_entries with the correct stream_id."""
    mock_fetch_entries = mocker.patch(
        "feedly_entries_processor.feedly_client.FeedlyClient.fetch_entries"
    )

    client = FeedlyClient(mock_feedly_session)
    # list() is necessary to consume the generator
    list(client.fetch_saved_entries())

    expected_stream_id = f"user/{mock_feedly_session.user.id}/tag/global.saved"
    mock_fetch_entries.assert_called_once_with(expected_stream_id)


def test_fetch_entries_raises_fetch_entries_error_on_request_exception(
    mock_feedly_session: MagicMock,
) -> None:
    """Test that FetchEntriesError is raised on a RequestException."""
    mock_feedly_session.do_api_request.side_effect = RequestException

    client = FeedlyClient(mock_feedly_session)
    with pytest.raises(FetchEntriesError):
        list(client.fetch_entries("dummy_stream_id"))


def test_fetch_entries_raises_fetch_entries_error_on_validation_error(
    mock_feedly_session: MagicMock,
) -> None:
    """Test that FetchEntriesError is raised on a ValidationError."""
    mock_feedly_session.do_api_request.return_value = {
        "items": [{"invalid_field": "foo"}]
    }

    client = FeedlyClient(mock_feedly_session)
    with pytest.raises(FetchEntriesError) as excinfo:
        list(client.fetch_entries("dummy_stream_id"))

    assert isinstance(excinfo.value.__cause__, ValidationError)

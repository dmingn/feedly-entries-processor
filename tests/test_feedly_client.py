"""Tests for the Feedly client."""

from unittest.mock import MagicMock

import pytest

from feedly_saved_entries_processor.feedly_client import (
    Entry,
    FeedlyClient,
    Origin,
    Summary,
)


@pytest.fixture
def mock_feedly_session() -> MagicMock:
    """Fixture for a mock FeedlySession."""
    session = MagicMock()
    session.user.id = "test_user_id"
    return session


def test_fetch_saved_entries_single_page(mock_feedly_session: MagicMock) -> None:
    """Test fetching saved entries with a single page of results."""
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
    entries = list(client.fetch_saved_entries())

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
            "streamId": "user/test_user_id/tag/global.saved",
            "count": "1000",
            "ranked": "oldest",
        },
    )


def test_fetch_saved_entries_multiple_pages(mock_feedly_session: MagicMock) -> None:
    """Test fetching saved entries with multiple pages of results."""
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
    entries = list(client.fetch_saved_entries())

    assert len(entries) == 4
    assert entries[0].id == "entry1"
    assert entries[1].id == "entry2"
    assert entries[2].id == "entry3"
    assert entries[3].id == "entry4"

    # Verify calls
    mock_feedly_session.do_api_request.assert_any_call(
        relative_url="/v3/streams/contents",
        params={
            "streamId": "user/test_user_id/tag/global.saved",
            "count": "1000",
            "ranked": "oldest",
        },
    )
    mock_feedly_session.do_api_request.assert_any_call(
        relative_url="/v3/streams/contents",
        params={
            "streamId": "user/test_user_id/tag/global.saved",
            "count": "1000",
            "ranked": "oldest",
            "continuation": "continuation1",
        },
    )
    assert mock_feedly_session.do_api_request.call_count == 2


def test_fetch_saved_entries_no_entries(mock_feedly_session: MagicMock) -> None:
    """Test fetching saved entries when no entries are returned."""
    mock_feedly_session.do_api_request.return_value = {
        "items": [],
        "continuation": None,
    }

    client = FeedlyClient(mock_feedly_session)
    entries = list(client.fetch_saved_entries())

    assert len(entries) == 0
    mock_feedly_session.do_api_request.assert_called_once()

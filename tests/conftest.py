"""Common fixtures for tests."""

import pytest

from feedly_entries_processor.feedly_client import Entry, Origin


@pytest.fixture
def mock_entry_with_origin() -> Entry:
    """Provide a mock Entry object with origin and stream_id."""
    return Entry(
        id="entry1",
        title="Test Entry",
        origin=Origin(
            html_url="http://example.com",
            stream_id="feed/test.com/1",
            title="Test Feed",
        ),
    )


@pytest.fixture
def mock_entry_without_origin() -> Entry:
    """Provide a mock Entry object without origin."""
    return Entry(
        id="entry2",
        title="Another Entry",
        origin=None,
    )

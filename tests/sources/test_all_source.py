"""Tests for AllSource."""

from unittest.mock import MagicMock

from feedly_entries_processor.feedly_client import FeedlyClient
from feedly_entries_processor.sources import AllSource


def test_all_source_fetch_entries_calls_client_with_correct_stream_id() -> None:
    """Test that AllSource.fetch_entries calls client.fetch_entries with the correct stream_id."""
    mock_client = MagicMock(spec=FeedlyClient)
    mock_client.user_id = "test_user_123"
    mock_client.fetch_entries.return_value = iter([])

    source = AllSource()
    list(source.fetch_entries(mock_client))

    expected_stream_id = "user/test_user_123/category/global.all"
    mock_client.fetch_entries.assert_called_once_with(expected_stream_id)

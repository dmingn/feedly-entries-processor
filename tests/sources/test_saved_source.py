"""Tests for SavedSource."""

from unittest.mock import MagicMock

from feedly_entries_processor.feedly_client import FeedlyClient
from feedly_entries_processor.sources import SavedSource


def test_saved_source_fetch_entries_calls_client_with_correct_stream_id() -> None:
    """Test that SavedSource.fetch_entries calls client.fetch_entries with the correct stream_id."""
    mock_client = MagicMock(spec=FeedlyClient)
    mock_client.user_id = "test_user_123"
    mock_client.fetch_entries.return_value = iter([])

    source = SavedSource()
    list(source.fetch_entries(mock_client))

    expected_stream_id = "user/test_user_123/tag/global.saved"
    mock_client.fetch_entries.assert_called_once_with(expected_stream_id)

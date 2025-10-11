"""Tests for the StreamIdInMatcher."""

import pytest
from pydantic import ValidationError

from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.matchers import StreamIdInMatcher


def test_stream_id_in_matcher_is_match_with_origin(
    mock_entry_with_origin: Entry,
) -> None:
    """Test StreamIdInMatcher when entry has origin and stream_id is in list."""
    matcher = StreamIdInMatcher(
        matcher_name="stream_id_in", stream_ids=("feed/test.com/1", "feed/test.com/2")
    )
    assert matcher.is_match(mock_entry_with_origin) is True


def test_stream_id_in_matcher_is_match_not_in_list(
    mock_entry_with_origin: Entry,
) -> None:
    """Test StreamIdInMatcher when entry has origin and stream_id is not in list."""
    matcher = StreamIdInMatcher(
        matcher_name="stream_id_in", stream_ids=("feed/test.com/99",)
    )
    assert matcher.is_match(mock_entry_with_origin) is False


def test_stream_id_in_matcher_is_match_without_origin(
    mock_entry_without_origin: Entry,
) -> None:
    """Test StreamIdInMatcher when entry does not have origin."""
    matcher = StreamIdInMatcher(
        matcher_name="stream_id_in", stream_ids=("feed/test.com/1",)
    )
    assert matcher.is_match(mock_entry_without_origin) is False


def test_stream_id_in_matcher_pydantic_instantiation() -> None:
    """Test that StreamIdInMatcher can be instantiated correctly by Pydantic."""
    matcher = StreamIdInMatcher.model_validate(
        {
            "matcher_name": "stream_id_in",
            "stream_ids": ("feed/test.com/1", "feed/test.com/2"),
        }
    )
    assert isinstance(matcher, StreamIdInMatcher)
    assert matcher.matcher_name == "stream_id_in"
    assert matcher.stream_ids == ("feed/test.com/1", "feed/test.com/2")


def test_stream_id_in_matcher_pydantic_validation_error() -> None:
    """Test that StreamIdInMatcher raises ValidationError for missing stream_ids."""
    with pytest.raises(ValidationError):
        StreamIdInMatcher.model_validate({"matcher_name": "stream_id_in"})


def test_stream_id_in_matcher_pydantic_validation_error_wrong_type() -> None:
    """Test that StreamIdInMatcher raises ValidationError for wrong type of stream_ids."""
    with pytest.raises(ValidationError):
        StreamIdInMatcher.model_validate(
            {"matcher_name": "stream_id_in", "stream_ids": "not_a_list"}
        )

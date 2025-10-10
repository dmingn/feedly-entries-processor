"""Tests for the rule_matcher module."""

import pytest
from pydantic import ValidationError

from feedly_entries_processor.feedly_client import Entry, Origin
from feedly_entries_processor.rule_matcher import AllMatcher, StreamIdInMatcher


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


# Tests for AllMatcher
def test_all_matcher_is_match(mock_entry_with_origin: Entry) -> None:
    """Test that AllMatcher always returns True."""
    matcher = AllMatcher(matcher_name="all")
    assert matcher.is_match(mock_entry_with_origin) is True


def test_all_matcher_pydantic_instantiation() -> None:
    """Test that AllMatcher can be instantiated correctly by Pydantic."""
    matcher = AllMatcher.model_validate({"matcher_name": "all"})
    assert isinstance(matcher, AllMatcher)
    assert matcher.matcher_name == "all"


# Tests for StreamIdInMatcher
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

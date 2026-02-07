"""Tests for the AllMatcher."""

from feedly_entries_processor.feedly_client import Entry
from feedly_entries_processor.matchers import AllMatcher


def test_all_matcher_is_match(mock_entry_with_origin: Entry) -> None:
    """Test that AllMatcher always returns True."""
    matcher = AllMatcher(matcher_name="all")
    assert matcher.is_match(mock_entry_with_origin) is True


def test_all_matcher_pydantic_instantiation() -> None:
    """Test that AllMatcher can be instantiated correctly by Pydantic."""
    matcher = AllMatcher.model_validate({"matcher_name": "all"})
    assert isinstance(matcher, AllMatcher)
    assert matcher.matcher_name == "all"

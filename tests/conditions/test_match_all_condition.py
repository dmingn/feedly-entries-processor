"""Tests for the MatchAllCondition."""

from feedly_entries_processor.conditions import MatchAllCondition
from feedly_entries_processor.feedly_client import Entry


def test_match_all_condition_is_match(mock_entry_with_origin: Entry) -> None:
    """Test that MatchAllCondition always returns True."""
    condition = MatchAllCondition(condition_name="match_all")
    assert condition.is_match(mock_entry_with_origin) is True


def test_match_all_condition_pydantic_instantiation() -> None:
    """Test that MatchAllCondition can be instantiated correctly by Pydantic."""
    condition = MatchAllCondition.model_validate({"condition_name": "match_all"})
    assert isinstance(condition, MatchAllCondition)
    assert condition.condition_name == "match_all"

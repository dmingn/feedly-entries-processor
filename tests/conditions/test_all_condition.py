"""Tests for the AllCondition."""

from feedly_entries_processor.conditions import AllCondition
from feedly_entries_processor.feedly_client import Entry


def test_all_condition_is_match(mock_entry_with_origin: Entry) -> None:
    """Test that AllCondition always returns True."""
    condition = AllCondition(condition_name="all")
    assert condition.is_match(mock_entry_with_origin) is True


def test_all_condition_pydantic_instantiation() -> None:
    """Test that AllCondition can be instantiated correctly by Pydantic."""
    condition = AllCondition.model_validate({"condition_name": "all"})
    assert isinstance(condition, AllCondition)
    assert condition.condition_name == "all"

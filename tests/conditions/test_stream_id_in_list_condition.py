"""Tests for the StreamIdInListCondition."""

import pytest
from pydantic import ValidationError

from feedly_entries_processor.conditions import StreamIdInListCondition
from feedly_entries_processor.feedly_client import Entry


def test_stream_id_in_list_condition_matches_with_origin(
    mock_entry_with_origin: Entry,
) -> None:
    """Test StreamIdInListCondition when entry has origin and stream_id is in list."""
    condition = StreamIdInListCondition(
        name="stream_id_in_list",
        stream_ids=frozenset({"feed/test.com/1", "feed/test.com/2"}),
    )
    assert condition.matches(mock_entry_with_origin) is True


def test_stream_id_in_list_condition_matches_not_in_list(
    mock_entry_with_origin: Entry,
) -> None:
    """Test StreamIdInListCondition when entry has origin and stream_id is not in list."""
    condition = StreamIdInListCondition(
        name="stream_id_in_list",
        stream_ids=frozenset({"feed/test.com/99"}),
    )
    assert condition.matches(mock_entry_with_origin) is False


def test_stream_id_in_list_condition_matches_without_origin(
    mock_entry_without_origin: Entry,
) -> None:
    """Test StreamIdInListCondition when entry does not have origin."""
    condition = StreamIdInListCondition(
        name="stream_id_in_list",
        stream_ids=frozenset({"feed/test.com/1"}),
    )
    assert condition.matches(mock_entry_without_origin) is False


def test_stream_id_in_list_condition_pydantic_instantiation() -> None:
    """Test that StreamIdInListCondition can be instantiated correctly by Pydantic."""
    condition = StreamIdInListCondition.model_validate(
        {
            "name": "stream_id_in_list",
            "stream_ids": ["feed/test.com/1", "feed/test.com/2"],
        }
    )
    assert isinstance(condition, StreamIdInListCondition)
    assert condition.name == "stream_id_in_list"
    assert condition.stream_ids == frozenset({"feed/test.com/1", "feed/test.com/2"})


def test_stream_id_in_list_condition_pydantic_validation_error() -> None:
    """Test that StreamIdInListCondition raises ValidationError for missing stream_ids."""
    with pytest.raises(ValidationError):
        StreamIdInListCondition.model_validate({"name": "stream_id_in_list"})


def test_stream_id_in_list_condition_pydantic_validation_error_wrong_type() -> None:
    """Test that StreamIdInListCondition raises ValidationError for wrong type of stream_ids."""
    with pytest.raises(ValidationError):
        StreamIdInListCondition.model_validate(
            {
                "name": "stream_id_in_list",
                "stream_ids": "not_a_list",
            }
        )

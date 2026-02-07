"""Tests for the StreamIdInCondition."""

import pytest
from pydantic import ValidationError

from feedly_entries_processor.conditions import StreamIdInCondition
from feedly_entries_processor.feedly_client import Entry


def test_stream_id_in_condition_is_match_with_origin(
    mock_entry_with_origin: Entry,
) -> None:
    """Test StreamIdInCondition when entry has origin and stream_id is in list."""
    condition = StreamIdInCondition(
        condition_name="stream_id_in",
        stream_ids=("feed/test.com/1", "feed/test.com/2"),
    )
    assert condition.is_match(mock_entry_with_origin) is True


def test_stream_id_in_condition_is_match_not_in_list(
    mock_entry_with_origin: Entry,
) -> None:
    """Test StreamIdInCondition when entry has origin and stream_id is not in list."""
    condition = StreamIdInCondition(
        condition_name="stream_id_in", stream_ids=("feed/test.com/99",)
    )
    assert condition.is_match(mock_entry_with_origin) is False


def test_stream_id_in_condition_is_match_without_origin(
    mock_entry_without_origin: Entry,
) -> None:
    """Test StreamIdInCondition when entry does not have origin."""
    condition = StreamIdInCondition(
        condition_name="stream_id_in", stream_ids=("feed/test.com/1",)
    )
    assert condition.is_match(mock_entry_without_origin) is False


def test_stream_id_in_condition_pydantic_instantiation() -> None:
    """Test that StreamIdInCondition can be instantiated correctly by Pydantic."""
    condition = StreamIdInCondition.model_validate(
        {
            "condition_name": "stream_id_in",
            "stream_ids": ("feed/test.com/1", "feed/test.com/2"),
        }
    )
    assert isinstance(condition, StreamIdInCondition)
    assert condition.condition_name == "stream_id_in"
    assert condition.stream_ids == ("feed/test.com/1", "feed/test.com/2")


def test_stream_id_in_condition_pydantic_validation_error() -> None:
    """Test that StreamIdInCondition raises ValidationError for missing stream_ids."""
    with pytest.raises(ValidationError):
        StreamIdInCondition.model_validate({"condition_name": "stream_id_in"})


def test_stream_id_in_condition_pydantic_validation_error_wrong_type() -> None:
    """Test that StreamIdInCondition raises ValidationError for wrong type of stream_ids."""
    with pytest.raises(ValidationError):
        StreamIdInCondition.model_validate(
            {"condition_name": "stream_id_in", "stream_ids": "not_a_list"}
        )

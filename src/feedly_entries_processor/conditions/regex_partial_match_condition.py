"""RegexPartialMatchCondition module."""

import re
from typing import Literal, assert_never

from pydantic import Field

from feedly_entries_processor.conditions.base_condition import BaseCondition
from feedly_entries_processor.feedly_client import Entry

FieldName = Literal["title", "author", "summary_contents"]


class RegexPartialMatchCondition(BaseCondition):
    """Condition that matches when any of the patterns are found in any of the specified fields."""

    name: Literal["regex_partial_match"] = "regex_partial_match"
    fields: tuple[FieldName, ...] = Field(min_length=1)
    patterns: tuple[str, ...] = Field(min_length=1)

    @staticmethod
    def _get_field_value(entry: Entry, field_name: FieldName) -> str | None:
        if field_name == "title":
            return entry.title
        if field_name == "author":
            return entry.author
        if field_name == "summary_contents":
            return entry.summary.content if entry.summary else None

        assert_never(field_name)

    def matches(self, entry: Entry) -> bool:
        """Return True if any of the entry's specified fields match any of the patterns."""
        for field_name in self.fields:
            value = self._get_field_value(entry, field_name)

            if value is None:
                continue

            for pattern in self.patterns:
                if re.search(pattern, value):
                    return True

        return False

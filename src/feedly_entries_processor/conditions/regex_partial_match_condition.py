"""RegexPartialMatchCondition module."""

import re
from typing import Literal

from pydantic import Field, field_validator

from feedly_entries_processor.conditions.base_condition import BaseCondition
from feedly_entries_processor.feedly_client import Entry


class RegexPartialMatchCondition(BaseCondition):
    """Condition that matches when any of the patterns are found in any of the specified fields."""

    name: Literal["regex_partial_match"] = "regex_partial_match"
    fields: list[Literal["title", "author", "summary_contents"]] = Field(min_length=1)
    patterns: list[str] = Field(min_length=1)

    @field_validator("fields", mode="after")
    @classmethod
    def check_fields_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure fields list is not empty."""
        if not v:
            msg = "fields must not be empty"
            raise ValueError(msg)
        return v

    @field_validator("patterns", mode="after")
    @classmethod
    def check_patterns_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure patterns list is not empty."""
        if not v:
            msg = "patterns must not be empty"
            raise ValueError(msg)
        return v

    def matches(self, entry: Entry) -> bool:
        """Return True if any of the entry's specified fields match any of the patterns."""
        field_values: list[str | None] = []
        for field_name in self.fields:
            if field_name == "title":
                field_values.append(entry.title)
            elif field_name == "author":
                field_values.append(entry.author)
            elif field_name == "summary_contents":
                field_values.append(entry.summary.content if entry.summary else None)

        for value in field_values:
            if value is None:
                continue
            for pattern in self.patterns:
                if re.search(pattern, value):
                    return True

        return False

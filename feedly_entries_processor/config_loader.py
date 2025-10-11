"""Configuration loading and validation for Feedly Entries Processor."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_yaml import parse_yaml_raw_as
from ruamel.yaml.error import YAMLError

from feedly_entries_processor.entry_processors.log_entry_processor import (
    LogEntryProcessor,
)
from feedly_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)
from feedly_entries_processor.rule_matcher import AllMatcher, StreamIdInMatcher


class Rule(BaseModel):
    """Defines a single processing rule for Feedly entries."""

    name: str
    source: Literal["saved"]
    match: AllMatcher | StreamIdInMatcher = Field(discriminator="matcher_name")
    processor: LogEntryProcessor | TodoistEntryProcessor = Field(
        discriminator="processor_name"
    )
    model_config = ConfigDict(frozen=True)


class Config(BaseModel):
    """Overall configuration for the Feedly Entries Processor."""

    rules: frozenset[Rule]
    model_config = ConfigDict(frozen=True)

    def __or__(self, other: "Config") -> "Config":
        """Combine two Config objects, merging their rules.

        Args:
            other: Another Config object to combine with.

        Returns
        -------
            A new Config object containing all unique rules from both original Config objects.
        """
        if not isinstance(other, Config):
            return NotImplemented

        return Config(rules=self.rules | other.rules)


def load_config(file_path: Path) -> Config:
    """Load and validate the configuration from a YAML file.

    Args:
        file_path: The path to the YAML configuration file.

    Returns
    -------
        A Config object representing the loaded configuration.

    Raises
    ------
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If there is an error parsing or validating the configuration file.
    """
    if not file_path.exists():
        msg = f"Configuration file not found: {file_path}"
        raise FileNotFoundError(msg)

    try:
        yaml_content = file_path.read_text(encoding="utf-8")
        return parse_yaml_raw_as(Config, yaml_content)
    except (YAMLError, ValidationError) as e:
        msg = f"Error parsing configuration file {file_path}: {e}"
        raise ValueError(msg) from e

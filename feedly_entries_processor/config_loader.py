"""Configuration loading and validation for Feedly Entries Processor."""

from collections.abc import Iterable
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    FilePath,
    validate_call,
)
from pydantic_yaml import parse_yaml_raw_as

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


@validate_call
def load_config_file(file_path: FilePath) -> Config:
    """Load and validate the configuration from a YAML file.

    Args:
        file_path: The path to the YAML configuration file.

    Returns
    -------
        A Config object representing the loaded configuration.

    Raises
    ------
        ValidationError: If the configuration file does not exist, or if there
                         is a Pydantic validation error within the configuration.
        YAMLError: If there is an error parsing the YAML content of the
                    configuration file (e.g., malformed YAML).
    """
    yaml_content = file_path.read_text(encoding="utf-8")
    return parse_yaml_raw_as(Config, yaml_content)


@validate_call
def load_config(paths: Iterable[FilePath | DirectoryPath]) -> Config:
    """Load and merge configuration from multiple YAML files in given paths.

    Args:
        paths: An iterable of file or directory paths containing YAML configuration files.

    Returns
    -------
        A Config object representing the merged configuration from all valid files.

    Raises
    ------
        ValidationError: If any configuration file does not exist, or if there
                         is a Pydantic validation error within any configuration.
        YAMLError: If there is an error parsing the YAML content of any
                    configuration file (e.g., malformed YAML).
    """
    config = Config(rules=frozenset())

    for path in paths:
        if path.is_file():
            config |= load_config_file(path)
        elif path.is_dir():
            for pattern in ("*.yml", "*.yaml"):
                for file_path in path.glob(pattern):
                    config |= load_config_file(file_path)

    return config

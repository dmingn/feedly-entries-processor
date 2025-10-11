"""Tests for the config_loader module."""

from pathlib import Path

import pytest

from feedly_entries_processor.config_loader import (
    Config,
    Rule,
    load_config,
    save_config,
)
from feedly_entries_processor.entry_processors.log_entry_processor import (
    LogEntryProcessor,
)
from feedly_entries_processor.rule_matcher import AllMatcher, StreamIdInMatcher


@pytest.fixture
def test_configs_path() -> Path:
    """Provide the base path to the test configuration files directory."""
    return Path(__file__).parent / "test_configs"


@pytest.fixture
def valid_config_file(test_configs_path: Path) -> Path:
    """Provide a path to a valid configuration file."""
    return test_configs_path / "valid_config.yaml"


@pytest.fixture
def invalid_yaml_file(test_configs_path: Path) -> Path:
    """Provide a path to an invalid YAML file."""
    return test_configs_path / "invalid_yaml.yaml"


@pytest.fixture
def invalid_schema_file(test_configs_path: Path) -> Path:
    """Provide a path to a YAML file with invalid schema."""
    return test_configs_path / "invalid_schema.yaml"


def test_load_config_success(valid_config_file: Path) -> None:
    """Test that a valid configuration file can be loaded successfully."""
    config = load_config(valid_config_file)

    assert isinstance(config, Config)
    expected_config = Config(
        rules=frozenset(
            (
                Rule(
                    name="Log Rule for Stream ID",
                    source="saved",
                    match=StreamIdInMatcher(
                        matcher_name="stream_id_in", stream_ids=("feed/test.com/3",)
                    ),
                    processor=LogEntryProcessor(processor_name="log", level="info"),
                ),
                Rule(
                    name="Log Rule for All Matcher",
                    source="saved",
                    match=AllMatcher(matcher_name="all"),
                    processor=LogEntryProcessor(processor_name="log", level="debug"),
                ),
            )
        )
    )
    assert config == expected_config


def test_load_config_file_not_found(tmp_path: Path) -> None:
    """Test that FileNotFoundError is raised for a non-existent file."""
    non_existent_file = tmp_path / "non_existent.yaml"
    with pytest.raises(FileNotFoundError):
        load_config(non_existent_file)


def test_load_config_invalid_yaml(invalid_yaml_file: Path) -> None:
    """Test that ValueError is raised for an invalid YAML file."""
    with pytest.raises(ValueError, match="Error parsing configuration file"):
        load_config(invalid_yaml_file)


def test_load_config_invalid_schema(invalid_schema_file: Path) -> None:
    """Test that ValueError is raised for a YAML file with invalid schema."""
    with pytest.raises(ValueError, match="Error parsing configuration file"):
        load_config(invalid_schema_file)


def test_save_config_and_load_back(tmp_path: Path) -> None:
    """Test that a Config object can be saved and loaded back correctly."""
    original_config = Config(
        rules=(
            Rule(
                name="Saved Rule",
                source="saved",
                match=StreamIdInMatcher(
                    matcher_name="stream_id_in", stream_ids=("feed/saved.com/1",)
                ),
                processor=LogEntryProcessor(
                    processor_name="log",
                    level="info",
                ),
            ),
        )
    )
    output_file = tmp_path / "saved_config.yaml"

    save_config(original_config, output_file)

    loaded_config = load_config(output_file)

    assert loaded_config == original_config

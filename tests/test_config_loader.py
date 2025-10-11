"""Tests for the config_loader module."""

from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_yaml import to_yaml_str
from ruamel.yaml.error import YAMLError

from feedly_entries_processor.config_loader import (
    Config,
    Rule,
    load_config,
    load_config_file,
)
from feedly_entries_processor.entry_processors import LogEntryProcessor
from feedly_entries_processor.matchers import AllMatcher, StreamIdInMatcher


def _save_config(config: Config, file_path: Path) -> None:
    """Save the configuration to a YAML file.

    Args:
        config: The Config object to save.
        file_path: The path to the YAML file where the configuration will be saved.
    """
    file_path.write_text(to_yaml_str(config), encoding="utf-8")


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


def test_load_config_file_success(valid_config_file: Path) -> None:
    """Test that a valid configuration file can be loaded successfully."""
    config = load_config_file(valid_config_file)

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


def test_load_config_file_file_not_found(tmp_path: Path) -> None:
    """Test that ValidationError is raised for a non-existent file."""
    non_existent_file = tmp_path / "non_existent.yaml"
    with pytest.raises(ValidationError, match="Path does not point to a file"):
        load_config_file(non_existent_file)


def test_load_config_file_invalid_yaml(invalid_yaml_file: Path) -> None:
    """Test that YAMLError is raised for an invalid YAML file."""
    with pytest.raises(YAMLError):
        load_config_file(invalid_yaml_file)


def test_load_config_file_invalid_schema(invalid_schema_file: Path) -> None:
    """Test that ValidationError is raised for a YAML file with invalid schema."""
    with pytest.raises(ValidationError, match="Field required"):
        load_config_file(invalid_schema_file)


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

    _save_config(original_config, output_file)

    loaded_config = load_config_file(output_file)

    assert loaded_config == original_config


def test_config_or_operator() -> None:
    """Test the | operator for combining two Config objects."""
    rule1 = Rule(
        name="Rule 1",
        source="saved",
        match=AllMatcher(matcher_name="all"),
        processor=LogEntryProcessor(processor_name="log", level="info"),
    )
    rule2 = Rule(
        name="Rule 2",
        source="saved",
        match=StreamIdInMatcher(
            matcher_name="stream_id_in", stream_ids=("feed/test.com/1",)
        ),
        processor=LogEntryProcessor(processor_name="log", level="debug"),
    )
    common_rule = Rule(
        name="Common Rule",
        source="saved",
        match=AllMatcher(matcher_name="all"),
        processor=LogEntryProcessor(processor_name="log", level="warning"),
    )

    config1 = Config(rules=frozenset([rule1]))
    config2 = Config(rules=frozenset([rule2]))
    config1_with_common = Config(rules=frozenset([rule1, common_rule]))
    config2_with_common = Config(rules=frozenset([rule2, common_rule]))

    # Test combining two disjoint configs
    combined_config = config1 | config2
    assert combined_config.rules == frozenset([rule1, rule2])

    # Test combining two configs with a common rule
    combined_config_with_common = config1_with_common | config2_with_common
    assert combined_config_with_common.rules == frozenset([rule1, rule2, common_rule])

    # Test that the original configs are not modified
    assert config1.rules == frozenset([rule1])
    assert config2.rules == frozenset([rule2])

    # Test combining with a non-Config object
    with pytest.raises(TypeError):
        config1 | "not a config"  # type: ignore[operator]


def test_load_config_from_directory_with_yaml_and_yml(tmp_path: Path) -> None:
    """Test that load_config correctly loads and merges configurations from .yaml and .yml files in a directory."""
    # Create a temporary directory structure
    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    # Create a .yaml file
    yaml_config_path = config_dir / "config1.yaml"
    yaml_rule = Rule(
        name="Yaml Rule",
        source="saved",
        match=AllMatcher(matcher_name="all"),
        processor=LogEntryProcessor(processor_name="log", level="info"),
    )
    _save_config(Config(rules=frozenset([yaml_rule])), yaml_config_path)

    # Create a .yml file
    yml_config_path = config_dir / "config2.yml"
    yml_rule = Rule(
        name="Yml Rule",
        source="saved",
        match=StreamIdInMatcher(
            matcher_name="stream_id_in", stream_ids=("feed/test.com/yml",)
        ),
        processor=LogEntryProcessor(processor_name="log", level="debug"),
    )
    _save_config(Config(rules=frozenset([yml_rule])), yml_config_path)

    # Create an invalid file to ensure it's skipped
    (config_dir / "invalid.txt").write_text("not a yaml", encoding="utf-8")

    # Load config from the directory
    loaded_config = load_config([config_dir])

    # Assert that both rules are loaded
    assert loaded_config.rules == frozenset([yaml_rule, yml_rule])


def test_load_config_with_mixed_paths(tmp_path: Path) -> None:
    """Test that load_config correctly handles a mix of file paths and directory paths."""
    # Create a temporary directory structure
    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    # Create a .yaml file in the directory
    dir_yaml_path = config_dir / "dir_config.yaml"
    dir_yaml_rule = Rule(
        name="Dir Yaml Rule",
        source="saved",
        match=AllMatcher(matcher_name="all"),
        processor=LogEntryProcessor(processor_name="log", level="info"),
    )
    _save_config(Config(rules=frozenset([dir_yaml_rule])), dir_yaml_path)

    # Create a standalone .yml file
    standalone_yml_path = tmp_path / "standalone_config.yml"
    standalone_yml_rule = Rule(
        name="Standalone Yml Rule",
        source="saved",
        match=StreamIdInMatcher(
            matcher_name="stream_id_in", stream_ids=("feed/standalone.com/yml",)
        ),
        processor=LogEntryProcessor(processor_name="log", level="debug"),
    )
    _save_config(Config(rules=frozenset([standalone_yml_rule])), standalone_yml_path)

    # Load config from mixed paths
    loaded_config = load_config([config_dir, standalone_yml_path])

    # Assert that all rules are loaded
    assert loaded_config.rules == frozenset([dir_yaml_rule, standalone_yml_rule])

    # Test with a non-existent file path, should raise ValidationError
    with pytest.raises(ValidationError, match="Path does not point to a file"):
        load_config([tmp_path / "non_existent.yaml"])

    # Test with a non-existent directory path, should raise ValidationError
    with pytest.raises(ValidationError, match="Path does not point to a directory"):
        load_config([tmp_path / "non_existent_dir"])

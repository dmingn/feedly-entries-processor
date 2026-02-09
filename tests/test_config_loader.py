"""Tests for the config_loader module."""

import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_yaml import to_yaml_str
from ruamel.yaml.error import YAMLError

from feedly_entries_processor.actions import AddTodoistTaskAction, LogAction
from feedly_entries_processor.conditions import (
    MatchAllCondition,
    StreamIdInListCondition,
)
from feedly_entries_processor.config_loader import (
    Config,
    Rule,
    load_config,
    load_config_file,
)
from feedly_entries_processor.exceptions import ConfigError
from feedly_entries_processor.sources import AllSource, SavedSource

TEST_CONFIGS_PATH = Path(__file__).parent / "test_configs"

# Defaults when not varying that dimension (used for round-trip coverage).
_DEFAULT_SOURCE = AllSource()
_DEFAULT_CONDITION = MatchAllCondition()
_DEFAULT_ACTION = LogAction()


_SOURCES = (AllSource(), SavedSource())
_CONDITIONS = (
    MatchAllCondition(),
    StreamIdInListCondition(stream_ids=frozenset({"stream_id"})),
)
_ACTIONS = (
    LogAction(),
    AddTodoistTaskAction(
        project_id="project_id",
        due_datetime=datetime.datetime(2026, 1, 1, 0, 0, 0, tzinfo=datetime.UTC),
        priority=1,
    ),
)


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
    return TEST_CONFIGS_PATH


@pytest.mark.parametrize(
    ("path", "cause_type", "message_contains"),
    [
        pytest.param(
            TEST_CONFIGS_PATH / "invalid_yaml.yaml", YAMLError, None, id="invalid_yaml"
        ),
        pytest.param(
            TEST_CONFIGS_PATH / "invalid_schema.yaml",
            ValidationError,
            "Field required",
            id="invalid_schema",
        ),
        pytest.param(
            TEST_CONFIGS_PATH / "non_existent.yaml",
            ValidationError,
            "Path does not point to a file",
            id="file_not_found",
        ),
    ],
)
def test_load_config_file_failure(
    path: Path,
    cause_type: type[Exception],
    message_contains: str | None,
) -> None:
    """Test that ConfigError is raised for invalid YAML, invalid schema, or missing file."""
    with pytest.raises(ConfigError) as exc_info:
        load_config_file(path)
    assert isinstance(exc_info.value.__cause__, cause_type)
    if message_contains is not None:
        assert message_contains in str(exc_info.value.__cause__)


@pytest.mark.parametrize(
    ("path_suffix", "message_contains"),
    [
        ("non_existent.yaml", "Path does not point to a file"),
        ("non_existent_dir", "Path does not point to a directory"),
    ],
)
def test_load_config_path_failure(
    tmp_path: Path, path_suffix: str, message_contains: str
) -> None:
    """Test that load_config raises ConfigError for non-existent file or directory."""
    path = tmp_path / path_suffix
    with pytest.raises(ConfigError) as exc_info:
        load_config([path])
    assert isinstance(exc_info.value.__cause__, ValidationError)
    assert message_contains in str(exc_info.value.__cause__)


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(
            Config(rules=frozenset([Rule(name=name, source=s, condition=c, action=a)])),
            id=name,
        )
        for (s, c, a) in frozenset(
            [(s, _DEFAULT_CONDITION, _DEFAULT_ACTION) for s in _SOURCES]
            + [(_DEFAULT_SOURCE, c, _DEFAULT_ACTION) for c in _CONDITIONS]
            + [(_DEFAULT_SOURCE, _DEFAULT_CONDITION, a) for a in _ACTIONS]
        )
        for name in [f"{type(s).__name__}_{type(c).__name__}_{type(a).__name__}"]
    ],
)
def test_config_round_trip(config: Config, tmp_path: Path) -> None:
    """Test that each Config round-trips: write to YAML, load back, assert equal."""
    path = tmp_path / "config.yaml"
    path.write_text(to_yaml_str(config), encoding="utf-8")
    loaded = load_config_file(path)
    assert loaded == config


def test_config_or_operator() -> None:
    """Test the | operator for combining two Config objects."""
    rule1 = Rule(
        name="Rule 1",
        source=SavedSource(),
        condition=MatchAllCondition(name="match_all"),
        action=LogAction(name="log", level="info"),
    )
    rule2 = Rule(
        name="Rule 2",
        source=SavedSource(),
        condition=StreamIdInListCondition(
            name="stream_id_in_list",
            stream_ids=frozenset({"feed/test.com/1"}),
        ),
        action=LogAction(name="log", level="debug"),
    )
    common_rule = Rule(
        name="Common Rule",
        source=SavedSource(),
        condition=MatchAllCondition(name="match_all"),
        action=LogAction(name="log", level="warning"),
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
        source=SavedSource(),
        condition=MatchAllCondition(name="match_all"),
        action=LogAction(name="log", level="info"),
    )
    _save_config(Config(rules=frozenset([yaml_rule])), yaml_config_path)

    # Create a .yml file
    yml_config_path = config_dir / "config2.yml"
    yml_rule = Rule(
        name="Yml Rule",
        source=SavedSource(),
        condition=StreamIdInListCondition(
            name="stream_id_in_list",
            stream_ids=frozenset({"feed/test.com/yml"}),
        ),
        action=LogAction(name="log", level="debug"),
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
        source=SavedSource(),
        condition=MatchAllCondition(name="match_all"),
        action=LogAction(name="log", level="info"),
    )
    _save_config(Config(rules=frozenset([dir_yaml_rule])), dir_yaml_path)

    # Create a standalone .yml file
    standalone_yml_path = tmp_path / "standalone_config.yml"
    standalone_yml_rule = Rule(
        name="Standalone Yml Rule",
        source=SavedSource(),
        condition=StreamIdInListCondition(
            name="stream_id_in_list",
            stream_ids=frozenset({"feed/standalone.com/yml"}),
        ),
        action=LogAction(name="log", level="debug"),
    )
    _save_config(Config(rules=frozenset([standalone_yml_rule])), standalone_yml_path)

    # Load config from mixed paths
    loaded_config = load_config([config_dir, standalone_yml_path])

    # Assert that all rules are loaded
    assert loaded_config.rules == frozenset([dir_yaml_rule, standalone_yml_rule])

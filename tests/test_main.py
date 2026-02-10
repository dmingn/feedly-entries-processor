"""Tests for the __main__ module."""

import json
from pathlib import Path

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from feedly_entries_processor.__main__ import app
from feedly_entries_processor.config_loader import Config

runner = CliRunner()


def test_main_runs_process_with_given_config_and_token_dir(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    # arrange
    mock_process = mocker.patch("feedly_entries_processor.__main__.process")

    config_file = tmp_path / "config.yml"
    config_file.touch()
    token_dir = tmp_path / "tokens"
    token_dir.mkdir()

    # act
    result = runner.invoke(
        app,
        [
            str(config_file),
            "--token-dir",
            str(token_dir),
        ],
    )

    # assert
    assert result.exit_code == 0, result.output
    mock_process.assert_called_once_with(
        config_files=[config_file], token_dir=token_dir
    )


def test_main_shows_config_schema_when_option_given() -> None:
    # act
    result = runner.invoke(app, ["--show-config-schema"])

    # assert
    assert result.exit_code == 0
    assert json.loads(result.stdout) == Config.model_json_schema()

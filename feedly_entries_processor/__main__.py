"""CLI application."""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

import logzero
import typer
from feedly.api_client.session import FeedlySession, FileAuthStore
from logzero import logger
from pydantic import ValidationError
from requests.exceptions import RequestException
from ruamel.yaml.error import YAMLError

from feedly_entries_processor.config_loader import Config, Rule, load_config
from feedly_entries_processor.feedly_client import Entry, FeedlyClient

app = typer.Typer()


@app.callback()
def main(
    *,
    json_log: Annotated[
        bool,
        typer.Option(help="Output logs in JSON format."),
    ] = False,
) -> None:
    """A CLI application to process Feedly entries."""  # noqa: D401
    if json_log:
        logzero.json()


def process_entry(entry: Entry, rule: Rule) -> None:
    """Process a single Feedly entry based on a rule."""
    try:
        if rule.match.is_match(entry):
            logger.info(
                f"Entry '{entry.title}' (URL: {entry.canonical_url}) matched rule '{rule.name}'."
            )
            try:
                rule.processor.process_entry(entry)
            except Exception:  # noqa: BLE001
                logger.exception(
                    f"Error processing entry '{entry.title}' (URL: {entry.canonical_url}) with rule '{rule.name}'."
                )
    except Exception:  # noqa: BLE001
        logger.exception(
            f"Error evaluating rule '{rule.name}' for entry '{entry.title}' (URL: {entry.canonical_url})."
        )


def process_entries(entries: Iterable[Entry], rules: Iterable[Rule]) -> None:
    """Process Feedly entries based on configured rules."""
    for entry in entries:
        for rule in rules:
            process_entry(entry, rule)


@app.command()
def process(
    config_files: Annotated[
        list[Path],
        typer.Argument(exists=True, file_okay=True, dir_okay=True),
    ],
    token_dir: Annotated[
        Path | None,
        typer.Option(exists=True, file_okay=False),
    ] = None,
) -> None:
    """Process entries."""
    if token_dir is None:
        token_dir = Path.home() / ".config" / "feedly"

    try:
        config = load_config(config_files)
        logger.info(
            f"Loaded {len(config.rules)} rules from {len(config_files)} sources"
        )
    except (YAMLError, ValidationError):
        logger.exception("Failed to load configuration.")
        raise typer.Exit(code=1) from None

    try:
        auth = FileAuthStore(token_dir=token_dir)
        feedly_session = FeedlySession(auth=auth)
        client = FeedlyClient(feedly_session=feedly_session)
    except (RequestException, ValidationError):
        logger.exception("Failed to initialize Feedly client.")
        raise typer.Exit(code=1) from None

    rules_for_saved_entries = frozenset(
        rule for rule in config.rules if rule.source == "saved"
    )
    try:
        saved_entries = client.fetch_saved_entries()
    except (RequestException, ValidationError):
        logger.exception("Failed to fetch saved entries.")
        raise typer.Exit(code=1) from None
    process_entries(entries=saved_entries, rules=rules_for_saved_entries)


@app.command()
def show_config_schema() -> None:
    """Show the JSON schema for the configuration file."""
    try:
        typer.echo(json.dumps(Config.model_json_schema(), indent=2))
    except TypeError:
        logger.exception("Failed to generate JSON schema for the configuration.")
        raise typer.Exit(code=1) from None


if __name__ == "__main__":
    try:
        app()
    except typer.Exit:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("An unexpected error occurred.")
        raise typer.Exit(code=1) from None

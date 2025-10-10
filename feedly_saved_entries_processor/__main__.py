"""CLI application."""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated

import typer
from feedly.api_client.session import FeedlySession, FileAuthStore
from logzero import logger

from feedly_saved_entries_processor.config_loader import Config, Rule, load_config
from feedly_saved_entries_processor.feedly_client import Entry, FeedlyClient

app = typer.Typer()


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
    config_file: Annotated[
        Path,
        typer.Option(exists=True, file_okay=True, dir_okay=False),
    ],
    token_dir: Annotated[
        Path | None,
        typer.Option(exists=True, file_okay=False),
    ] = None,
) -> None:
    """Process saved entries."""
    if token_dir is None:
        token_dir = Path.home() / ".config" / "feedly"

    config = load_config(config_file)
    logger.info(f"Loaded {len(config.rules)} rules from {config_file}")

    auth = FileAuthStore(token_dir=token_dir)
    feedly_session = FeedlySession(auth=auth)
    client = FeedlyClient(feedly_session=feedly_session)

    rules_for_saved_entries = tuple(
        rule for rule in config.rules if rule.source == "saved"
    )
    saved_entries = client.fetch_saved_entries()
    process_entries(entries=saved_entries, rules=rules_for_saved_entries)


@app.command()
def show_config_schema() -> None:
    """Show the JSON schema for the configuration file."""
    typer.echo(json.dumps(Config.model_json_schema(), indent=2))


if __name__ == "__main__":
    app()

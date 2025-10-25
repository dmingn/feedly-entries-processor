"""Module for processing Feedly entries."""

from collections.abc import Iterable
from pathlib import Path

import typer
from feedly.api_client.session import FeedlySession, FileAuthStore
from logzero import logger
from pydantic import ValidationError
from requests.exceptions import RequestException
from ruamel.yaml.error import YAMLError

from feedly_entries_processor.config_loader import Rule, load_config
from feedly_entries_processor.feedly_client import Entry, FeedlyClient


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


def process(config_files: list[Path], token_dir: Path) -> None:
    """Process entries."""
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

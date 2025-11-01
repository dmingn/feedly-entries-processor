"""Module for processing Feedly entries."""

from collections.abc import Iterable
from pathlib import Path

from logzero import logger

from feedly_entries_processor.config_loader import Rule, load_config
from feedly_entries_processor.feedly_client import Entry, create_feedly_client


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
    config = load_config(config_files)
    logger.info(f"Loaded {len(config.rules)} rules from {len(config_files)} sources")

    client = create_feedly_client(token_dir)

    rules_for_saved_entries = frozenset(
        rule for rule in config.rules if rule.source == "saved"
    )
    saved_entries = client.fetch_saved_entries()
    process_entries(entries=saved_entries, rules=rules_for_saved_entries)

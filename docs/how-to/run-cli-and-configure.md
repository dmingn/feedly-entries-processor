## How to run the CLI and configure rules

This guide shows different ways to run `feedly-entries-processor` and how to structure your YAML configuration.

For details of the YAML schema itself, see the configuration reference in [`configuration.md`](../reference/configuration.md).

## Running the CLI

### Single config file

Run the processor with a single YAML configuration file:

```bash
feedly-entries-processor config.yaml
```

### Multiple files and directories

You can pass multiple files and/or directories. Rules are merged:

```bash
feedly-entries-processor config1.yaml config2.yaml ./rules/
```

### Custom token directory

By default, tokens are read from `~/.config/feedly`. To use a different directory, pass `--token-dir`:

```bash
feedly-entries-processor --token-dir /path/to/tokens config.yaml
```

### JSON log output

To emit JSON-formatted logs, use `--json-log`:

```bash
feedly-entries-processor --json-log config.yaml
```

### Show configuration schema

To view the full JSON schema for the configuration, run:

```bash
feedly-entries-processor --show-config-schema
```

## Basic configuration structure

A configuration file contains a top-level `rules` list. Each rule has:

- `name`: human-friendly rule name
- `source`: where to read entries from (for example `saved` or `all`)
- `condition`: how to decide whether an entry matches
- `action`: what to do when an entry matches

See [`configuration.md`](../reference/configuration.md) for full details of available conditions and actions.

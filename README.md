# feedly-entries-processor

A Python CLI tool that fetches entries from Feedly (saved entries or the All feed) and processes them based on rules defined in YAML. You combine conditions and actions to route articles to actions such as logging or adding tasks to Todoist.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

For example, install from the repository using [pipx](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/dmingn/feedly-entries-processor/
```

## Feedly Authentication

The tool uses the [feedly-client](https://github.com/feedly/python-api-client) `FileAuthStore` format. By default, it reads tokens from `~/.config/feedly`. Place `access.token` and `refresh.token` in that directory. Obtain these tokens via the Feedly Developer Token or OAuth flow (see the [Feedly Python API client](https://github.com/feedly/python-api-client) documentation).

To use a different directory, pass `--token-dir`:

```bash
feedly-entries-processor --token-dir /path/to/tokens config.yaml
```

## Configuration

Configuration is written in YAML. Each rule has a `name`, a `source` (either `saved` for saved entries or `all` for the All feed / global.all), a `condition` block, and an `action` block.

### Conditions

| Name                | Description                         | Parameters                    |
| ------------------- | ----------------------------------- | ----------------------------- |
| `match_all`         | Matches all entries                 | None                          |
| `stream_id_in_list` | Matches entries in given stream IDs | `stream_ids`: list of strings |

### Actions

| Name               | Description                     | Parameters                                                |
| ------------------ | ------------------------------- | --------------------------------------------------------- |
| `log`              | Logs entry details              | `level`: `info`, `debug`, `warning`, or `error`           |
| `add_todoist_task` | Adds entry as a task in Todoist | `project_id` (required), `due_datetime`, `priority` (1–4) |

When using the Todoist action, set the `TODOIST_API_TOKEN` environment variable.

To view the full JSON schema for the configuration, run:

```bash
feedly-entries-processor --show-config-schema
```

### Example Configuration

```yaml
rules:
  - name: "Log saved entries from specific feed"
    source:
      name: "saved"
    condition:
      name: "stream_id_in_list"
      stream_ids:
        - "feed/example.com/123"
    action:
      name: "log"
      level: "info"

  - name: "Add all saved entries to Todoist"
    source:
      name: "saved"
    condition:
      name: "match_all"
    action:
      name: "add_todoist_task"
      project_id: "YOUR_PROJECT_ID"

  - name: "Log entries from All feed"
    source:
      name: "all"
    condition:
      name: "match_all"
    action:
      name: "log"
      level: "info"
```

## Usage

```bash
# Single config file
feedly-entries-processor config.yaml

# Multiple files and/or directories (rules are merged)
feedly-entries-processor config1.yaml config2.yaml ./rules/

# Custom token directory
feedly-entries-processor --token-dir /path/to/tokens config.yaml

# JSON log output
feedly-entries-processor --json-log config.yaml

# Show configuration schema
feedly-entries-processor --show-config-schema
```

## Development

- Run `uv sync` to set up dependencies.
- Run `make format-and-check` for formatting, linting, type checking, and tests.

See [AGENTS.md](AGENTS.md) for additional development guidelines.

## License

See [LICENSE](LICENSE).

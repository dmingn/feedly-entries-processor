## Configuration reference

This document describes the YAML configuration format for `feedly-entries-processor`.

Configuration is written in YAML. Each rule has a `name`, a `source`, a `condition` block, and an `action` block.

The `source` controls where entries are fetched from:

- `saved` for saved entries
- `all` for the All feed (`global.all`)

### Conditions

Each rule has a condition that determines whether it matches a given entry.

Available condition types:

| Name                | Description                         | Parameters                    |
| ------------------- | ----------------------------------- | ----------------------------- |
| `match_all`         | Matches all entries                 | None                          |
| `stream_id_in_list` | Matches entries in given stream IDs | `stream_ids`: list of strings |

### Actions

Each rule has an action that is executed when the condition matches.

Available action types:

| Name               | Description                     | Parameters                                                |
| ------------------ | ------------------------------- | --------------------------------------------------------- |
| `log`              | Logs entry details              | `level`: `info`, `debug`, `warning`, or `error`           |
| `add_todoist_task` | Adds entry as a task in Todoist | `project_id` (required), `due_datetime`, `priority` (1–4) |

When using the `add_todoist_task` action, set the `TODOIST_API_TOKEN` environment variable (or add it to a `.env` file).

### Schema

To view the full JSON schema for the configuration, run:

```bash
feedly-entries-processor --show-config-schema
```

### Example configuration

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

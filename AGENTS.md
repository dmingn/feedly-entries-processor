# AGENTS.md

This document provides guidelines and context for AI coding agents working on this project.

## Dev environment tips

This project assumes a Python development environment.

- **Python Version**: Refer to the `.python-version` file in the project root for the recommended Python version.
- **Dependency Management**: `uv` is used for dependency management and virtual environment creation.
- **Environment Setup**: To set up the project's virtual environment and install/sync dependencies, run:
  ```bash
  uv sync
  ```
  This command will create a virtual environment (if one doesn't exist) and install/sync all required packages as per `uv.lock`.

## Testing Instructions

To ensure code quality and adherence to standards, the agent SHOULD execute `make format-and-check` before submitting changes. This command runs formatting, linting, type checking, and unit tests.

## Language Policy

- **Development Language**: All code, documentation (including code comments), and commit messages MUST be written in English.
- **Conversational Language**: The language used for communication and conversation with the user should match the language the user is using.

## Commit Message Generation

When creating a commit message, the agent MUST adhere to the following rules:

1.  **Base on Git Diff Only:** The commit message MUST be based solely on the output of `git diff --staged` or `git diff HEAD`. The agent MUST ignore conversation history and work logs.
2.  **Follow Conventional Commits:** The commit message MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Naming Conventions for Rule Components

Rules are made of **conditions** (when to match) and **actions** (what to do). Use the following naming rules when adding or renaming them.

### Conditions

- **Class name**: Describe what is being matched (e.g. `MatchAllCondition`, `StreamIdInListCondition`). Verb-first is optional but can improve clarity.
- **File name**: Must match the class name in snake_case only (e.g. class `MatchAllCondition` → file `match_all_condition.py`, class `StreamIdInListCondition` → file `stream_id_in_list_condition.py`).
- **Config key `condition_name`**: Must match the class name with the `Condition` suffix removed, in snake_case (e.g. class `MatchAllCondition` → `condition_name: "match_all"`, class `StreamIdInListCondition` → `condition_name: "stream_id_in_list"`). Changing it is a breaking change.

### Actions

- **Class name**: **Verb-first** so the name reads as “what this action does” (e.g. `LogAction`, `AddTodoistTaskAction`).
- **File name**: Must match the class name in snake_case only (e.g. class `LogAction` → file `log_action.py`, class `AddTodoistTaskAction` → file `add_todoist_task_action.py`).
- **Config key `action_name`**: Must match the class name with the `Action` suffix removed, in snake_case (e.g. class `LogAction` → `action_name: "log"`, class `AddTodoistTaskAction` → `action_name: "add_todoist_task"`). Changing it is a breaking change.

### General

- When adding new conditions or actions, follow the conventions above. Use `git mv` when renaming files so history is preserved.

# AGENTS.md

This document provides guidelines and context for AI coding agents working on this project.

## Dev environment tips

This project assumes a Python development environment.

- **Python Version**: Refer to the `.python-version` file in the project root for the recommended Python version.
- **Dependency Management**: `poetry` is used for dependency management and virtual environment creation.
- **Environment Setup**: To set up the project's virtual environment and install/sync dependencies, run:
  ```bash
  poetry sync
  ```
  This command will create a virtual environment (if one doesn't exist) and install/sync all required packages as per `poetry.lock`.

## Testing Instructions

To ensure code quality and adherence to standards, the agent SHOULD execute `make format-and-check` before submitting changes. This command runs formatting, linting, type checking, and unit tests.

## Language Policy

- **Development Language**: All code, documentation (including code comments), and commit messages MUST be written in English.
- **Conversational Language**: The language used for communication and conversation with the user should match the language the user is using.

## Commit Message Generation

When creating a commit message, the agent MUST adhere to the following rules:

1.  **Base on Git Diff Only:** The commit message MUST be based solely on the output of `git diff --staged` or `git diff HEAD`. The agent MUST ignore conversation history and work logs.
2.  **Follow Conventional Commits:** The commit message MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

# AGENTS.md

This document provides guidelines and context for AI coding agents working on this project.

## Dev environment tips

For developer-facing instructions on setting up the Python environment and running checks, see `docs/how-to/develop-and-test.md`.

## Testing Instructions

To ensure code quality and adherence to standards, the agent SHOULD execute `make format-and-check` before submitting changes. This command runs formatting, linting, type checking, and unit tests.

For a developer-facing overview of how to run checks and tests, see `docs/how-to/develop-and-test.md`.

## Testing Conventions

For the canonical description of testing conventions for this project, see the “Testing conventions” section in `docs/how-to/develop-and-test.md`.

## Language Policy

- **Development Language**: All code, documentation (including code comments), and commit messages MUST be written in English.
- **Conversational Language**: The language used for communication and conversation with the user should match the language the user is using.

## Commit Message Generation

When creating a commit message, the agent MUST adhere to the following rules:

1.  **Base on Git Diff Only:** The commit message MUST be based solely on the output of `git diff --staged` or `git diff HEAD`. The agent MUST ignore conversation history and work logs.
2.  **Follow Conventional Commits:** The commit message MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Naming Conventions for Rule Components

For naming conventions when adding or renaming conditions and actions in code, see `docs/how-to/add-rule-components.md`.

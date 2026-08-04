# Test Setup

This document describes how to set up and run tests for this repository.

## About

This repo is a lightweight scratch space used for experimenting with GitHub
Copilot workflows and sandbox tooling. It does not currently ship a specific
language runtime or test framework — the steps below are a general guide to
get a testing environment running once code is added, and to keep things
consistent as the project grows.

## Prerequisites

- Git
- A recent version of the language runtime your changes use (e.g. Node.js,
  Python, Go) — install via your system package manager or a version manager
  (`nvm`, `pyenv`, etc.) as appropriate.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/martinajir/test.git
   cd test
   ```
2. Install dependencies for whichever tooling your changes introduce, e.g.:
   ```bash
   npm install        # Node.js projects
   pip install -r requirements.txt   # Python projects
   go mod download     # Go projects
   ```

## Running Tests

Run the test suite for your language/framework, for example:

```bash
npm test             # Node.js
pytest                # Python
go test ./...         # Go
```

If a `Makefile` or CI workflow is present, prefer its `test` target so local
runs match CI:

```bash
make test
```

## Adding New Tests

- Place tests alongside the code they cover, or in a `tests/`/`test/`
  directory following the convention of the chosen framework.
- Keep tests small, deterministic, and independent of external services.
- Update this document if the setup or run commands change.

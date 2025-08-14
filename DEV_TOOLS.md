# Development Tools

This project uses various tools to maintain code quality:

## Quick Setup

To quickly configure the development environment:

```bash
make setup
```

## Development Dependencies Installation

```bash
# Production dependencies only
make install

# Development dependencies
make install-dev
```

## Pre-commit Hooks

Pre-commit hooks are automatically executed on each commit to verify code quality.

### Installation

```bash
make pre-commit-install
```

### Manual execution on all files

```bash
make pre-commit
```

## Formatting and Linting

### Automatic formatting

```bash
make format
```

### Complete linting

```bash
make lint
```

### Auto-fix linting issues

```bash
make lint-fix
```

## Tests

### Running tests

```bash
make test
```

### Tests with coverage

```bash
make test-cov
```

## Available Makefile Commands

- `make setup` - Sets up the complete development environment
- `make install` - Installs production dependencies
- `make install-dev` - Installs development dependencies
- `make format` - Formats code with black and isort
- `make lint` - Runs all linting checks
- `make lint-fix` - Runs linting and automatically fixes issues
- `make test` - Runs tests
- `make test-cov` - Runs tests with coverage
- `make pre-commit` - Runs pre-commit on all files
- `make pre-commit-install` - Installs pre-commit hooks
- `make clean` - Cleans cache and temporary files

## Linting and Formatting Tools

### Black - Code formatting

```bash
black edge_mining/ tests/
```

### isort - Import sorting

```bash
isort edge_mining/ tests/
```

### flake8 - Linting

```bash
flake8 edge_mining/ tests/
```

### mypy - Type checking

```bash
mypy edge_mining/
```

### bandit - Security check

```bash
bandit -r edge_mining/
```

## Configurations

- **Black**: Configured in `pyproject.toml` with 88 character line length
- **isort**: Configured to be compatible with Black
- **flake8**: Configured in `.flake8` with exclusions for specific directories and 120 character line length
- **mypy**: Configured in `mypy.ini` with type checking settings
- **pre-commit**: Configured in `.pre-commit-config.yaml` with all necessary hooks
- **pytest**: Configured in `pyproject.toml` for testing and coverage

## Troubleshooting

If pre-commit doesn't work properly:

1. Make sure git is initialized: `git init`
2. Reinstall pre-commit: `make pre-commit-install`
3. Update hooks: `pre-commit autoupdate`

If you have dependency issues:

1. Clean the environment: `make clean`
2. Recreate the virtual environment: `python -m venv .venv`
3. Reinstall dependencies: `make setup`

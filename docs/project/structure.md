# Project Structure

This page explains the structure of the ClassCharts Calendar Sync project files and directories.

## Directory Structure

```text
.
├── .github/workflows/     # GitHub Actions CI/CD workflows
│   ├── sam-deploy.yml    # Automated deployment workflow
│   └── test.yml          # Automated testing workflow
├── tests/                # Test files
│   ├── conftest.py       # Test configuration and fixtures
│   └── test_main.py      # Main application tests
├── .aws-sam/            # SAM build artifacts (generated)
├── .gitignore            # Git ignore file
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE               # MIT License file
├── README.md             # Project documentation
├── config.py             # Configuration settings
├── main.py               # Lambda function core code
├── pytest.ini            # Pytest configuration
├── requirements.txt      # Python dependencies
├── samconfig.toml        # SAM CLI configuration
└── template.yaml         # SAM template for AWS resources
```

## Key Files and Components

### Core Files

| File | Description |
|------|-------------|
| `main.py` | The main application code that runs in the Lambda function |
| `config.py` | Configuration module that manages environment variables and defaults |
| `template.yaml` | SAM template that defines all AWS resources |
| `requirements.txt` | Python package dependencies |

### Configuration Files

| File | Description |
|------|-------------|
| `samconfig.toml` | SAM CLI configuration for deployments |
| `pytest.ini` | Configuration for the pytest testing framework |
| `.gitignore` | Specifies files to exclude from Git version control |

### Documentation Files

| File | Description |
|------|-------------|
| `README.md` | Basic project overview and quick start guide |
| `CONTRIBUTING.md` | Guidelines for contributing to the project |
| `LICENSE` | MIT License for the project |

### Test Files

| File | Description |
|------|-------------|
| `tests/conftest.py` | Pytest fixtures and configuration |
| `tests/test_main.py` | Unit tests for the main application code |

### GitHub Workflows

| File | Description |
|------|-------------|
| `.github/workflows/test.yml` | Runs automated tests on pull requests and pushes |
| `.github/workflows/sam-deploy.yml` | Deploys the application to AWS on pushes to the main branch |

## Code Organization

The project follows a simple structure:

- `main.py` contains all the application logic, including:
  - `get_secrets()` - Retrieves credentials from AWS Secrets Manager
  - `generate_calendar_for_student()` - Creates calendars for each student
  - `lambda_handler()` - Main entry point for the Lambda function

- `config.py` centralizes all configuration settings, with:
  - Environment variables with defaults
  - Constants for ClassCharts API interactions
  - Path templates for file storage
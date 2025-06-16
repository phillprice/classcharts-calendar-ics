# Contributing to ClassCharts Calendar Sync

Thank you for your interest in contributing to this project!

## Running Tests

This project uses pytest for testing. To run the tests locally:

```bash
# Install test dependencies
pip install pytest pytest-mock pytest-cov moto freezegun responses

# Run tests with coverage report
pytest --cov=main tests/
```

## CI/CD with GitHub Actions

This repository is configured with GitHub Actions that automatically:

1. Run tests on every push to the `main` branch and on pull requests
2. Deploy the application using AWS SAM (only on manual trigger or push to `main`)

### Setting up GitHub Secrets for Deployment

To enable automatic deployment via GitHub Actions, you need to add the following secrets to your GitHub repository:

1. `AWS_ACCESS_KEY_ID` - Your AWS access key with permissions to deploy
2. `AWS_SECRET_ACCESS_KEY` - Your AWS secret access key

### Manual Deployment

You can also manually trigger the deployment workflow in GitHub by:

1. Going to the "Actions" tab in your GitHub repository
2. Selecting the "Deploy with SAM" workflow
3. Clicking "Run workflow"

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Include type hints where appropriate

## Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request
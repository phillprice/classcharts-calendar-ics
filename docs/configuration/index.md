# Configuration

The ClassCharts Calendar Sync application uses a layered configuration approach:

## Configuration Layers

| Layer | Purpose | How to Configure |
|-------|---------|------------------|
| **Environment Variables** | Runtime configuration | Set during deployment or for local testing |
| **AWS Secrets Manager** | Sensitive credentials | Securely store ClassCharts credentials |
| **SAM Parameters** | Deployment configuration | Override during `sam deploy` |

## Configuration Files

| File | Purpose | Notes |
|------|---------|-------|
| `config.py` | Central configuration module | Contains defaults with environment variable overrides |
| `template.yaml` | SAM infrastructure definition | Defines AWS resources and their configuration |

## Overview of Configuration Areas

### Environment Variables

The application uses environment variables for runtime configuration. These can be set:
- During deployment via SAM template
- For local development via shell environment
- For local testing via environment variable overrides

[Learn more about Environment Variables →](environment-variables.md)

### AWS Secrets Manager

Sensitive credentials like ClassCharts login information are stored in AWS Secrets Manager to keep them secure and separate from the codebase.

[Learn more about AWS Secrets Manager configuration →](secrets-manager.md)

### SAM Parameters

When deploying with AWS SAM, you can customize various aspects of the application, such as:
- S3 bucket name
- Calendar filename templates
- Secret name paths

[Learn more about SAM Parameters →](sam-parameters.md)